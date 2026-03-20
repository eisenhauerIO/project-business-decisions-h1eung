#!/usr/bin/env python3
"""
Extension: Varying q Beyond the Paper's Range
==============================================
Auerbach, Guo, Tabord-Meehan (2026) — Empirical Application

The paper reports permutation test p-values only at q = 5, 10, 20.
This extension computes p-values across q = 1, 2, 3, 5, 8, 10, 15, 20, 25, 30, 35
for both comparisons (H0: knife=fork, H0: fork=spoon).

Key design: the expensive find_NN computations (75 villages × 3 configs) are
cached once (~5–10 min), then the q-loop runs zip_race + CvM + B=999
permutations for each q value (seconds per q value).

Outputs:
  extension_vary_q.txt  — table of p-values by q
  extension_vary_q.eps  — plot of p-value vs q for both comparisons
"""

import numpy as np
import networkx as nx
import networkx.algorithms.isomorphism as iso
import random
import copy
import pandas as pd
import csv
from itertools import chain
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from timeit import default_timer as timer
from decimal import Decimal
import scipy.stats as st
import igraph as ig
import os
import sys

# ---------------------------------------------------------------------------
# Path setup: data is in Empirical-Application, outputs go here
# ---------------------------------------------------------------------------
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(SCRIPT_DIR, '..', 'Empirical-Application')
OUT_DIR = SCRIPT_DIR

# ---------------------------------------------------------------------------
# All class/function definitions (copied verbatim from empirical-application.py)
# ---------------------------------------------------------------------------

class root_network(object):
    def __init__(self, root, network):
        new_network = copy.deepcopy(network)
        attrs = {k:{'is_root': i} for (k, i) in [(x, x in root) for x in list(new_network)]}
        edge_attrs = {k:{'is_root': i} for (k, i) in [(x, x in root.edges) for x in list(new_network.edges)]}
        nx.set_node_attributes(new_network, attrs)
        nx.set_edge_attributes(new_network, edge_attrs)
        self.root = root
        self.network = new_network
        if list(root.edges) == []:
            if 'favour' in network.nodes[list(root.nodes)[0]]:
                self.favour = network.nodes[list(root.nodes)[0]]['favour']
        if list(root.edges) != []:
            if 'favour' in network.edges[list(root.edges)[0]]:
                self.favour = network.edges[list(root.edges)[0]]['favour']

    def root_nbhd(self, k):
        node_list = []
        for node in list(self.root):
            node_list += nx.ego_graph(self.network, node, k).nodes
        sub_network = self.network.subgraph(node_list)
        return root_network(self.root, sub_network)

    def draw_igraph(self, ax):
        g = ig.Graph.from_networkx(self.network)
        g_1 = ig.Graph.from_networkx(self.root_nbhd(1).network)
        root_index_g = g.vs["is_root"].index(True)
        layout = g.layout_reingold_tilford(mode="all", root=[root_index_g])
        layout.rotate(270)
        root_node_list = [g.vs[i]["_nx_name"] for i in range(len(g.vs["_nx_name"])) if g.vs[i]["is_root"] == True]
        nbhd1_nodes_list = [g_1.vs[i]["_nx_name"] for i in range(len(g_1.vs["_nx_name"])) if g_1.vs[i]["is_root"] == False]
        nbhd2_nodes_list = [g.vs[i]["_nx_name"] for i in range(len(g.vs["_nx_name"])) if g.vs[i]["_nx_name"] not in nbhd1_nodes_list and g.vs[i]["is_root"] == False]
        nodes_list = g.vs["_nx_name"]
        vertex_size = [0]*len(nodes_list)
        vertex_shape = [""]*len(nodes_list)
        for i in range(len(nodes_list)):
            if g.vs[i]["is_root"] == True:
                vertex_size[i] = 50
                vertex_shape[i] = "diamond"
            elif g.vs[i]["_nx_name"] in nbhd1_nodes_list:
                vertex_size[i] = 30
                vertex_shape[i] = "circle"
            else:
                vertex_size[i] = 5
                vertex_shape[i] = "circle"
        ig.plot(g, layout=layout, target=ax,
                vertex_size=vertex_size,
                vertex_color="light blue",
                edge_width=[1],
                vertex_shape=vertex_shape)


def r_network_distance(R1, R2, max_radius, min_radius=0):
    for d in range(min_radius + 1, max_radius + 2):
        if d == max_radius + 1:
            return 1 / (max_radius + 1)
        R1_nbhd = R1.root_nbhd(d)
        R2_nbhd = R2.root_nbhd(d)
        if r_is_isomorphic(R1_nbhd, R2_nbhd) == False:
            return 1 / d
    return 1 / (max_radius + 1)


def r_is_isomorphic(R1, R2):
    G1 = R1.network
    G2 = R2.network
    if nx.faster_could_be_isomorphic(G1, G2) == False:
        return False
    else:
        nm = iso.categorical_node_match('is_root', 0)
        nm_edge = iso.categorical_edge_match('is_root', 0)
        return nx.is_isomorphic(G1, G2, node_match=nm, edge_match=nm_edge)


def make_R_list_nodes(G):
    R_list = []
    for n in G.nodes:
        R = root_network(G.subgraph(n), G)
        R_list.append(R)
    return R_list


def CvM(data1, data2):
    n = len(data1)
    m = len(data2)
    combined = np.concatenate((data1, data2))
    combined_sorted = np.sort(combined)
    ecdf1 = np.searchsorted(np.sort(data1), combined_sorted, side='right') / n
    ecdf2 = np.searchsorted(np.sort(data2), combined_sorted, side='right') / m
    return np.sum((ecdf1 - ecdf2) ** 2)


def zip_race(idx_list1, idx_list2, q):
    list1 = []
    list2 = []
    for i in range(q):
        list1.append(idx_list1[i])
        idx_list2 = np.delete(idx_list2, np.where(idx_list2 == idx_list1[i]))
        list2.append(idx_list2[i])
        idx_list1 = np.delete(idx_list1, np.where(idx_list1 == idx_list2[i]))
    return np.array(list1), np.array(list2)


def find_NN(R, R_list, max_radius):
    closest_nbh = R_list[0]
    closest_nbh_dist = r_network_distance(R, closest_nbh, max_radius)
    for R2 in R_list[1:]:
        if int(np.floor(1 / closest_nbh_dist)) - 1 == max_radius:
            break
        else:
            dist = r_network_distance(R, R2, max_radius,
                                      int(np.floor(1 / closest_nbh_dist)) - 1)
        if dist < closest_nbh_dist:
            closest_nbh = R2
            closest_nbh_dist = dist
    return closest_nbh, closest_nbh_dist


def gen_data(T, m, coeff=[0, 0, 0], seed=0):
    np.random.seed(seed)
    random.seed(seed)
    G_list = []
    for i in range(T):
        G = nx.erdos_renyi_graph(m, 2 / m)
        for n in G.nodes:
            R = root_network(G.subgraph(n), G)
            G1 = R.root_nbhd(1).network
            G2 = R.root_nbhd(2).network
            G3 = R.root_nbhd(3).network
            clust_0 = nx.average_clustering(G1)
            clust_1 = nx.average_clustering(G2)
            clust_2 = nx.average_clustering(G3)
            deg_0 = sum(dict(G1.degree()).values()) / len(G1)
            deg_1 = sum(dict(G2.degree()).values()) / len(G2)
            deg_2 = sum(dict(G3.degree()).values()) / len(G3)
            Y = coeff[0] * (deg_0 + 2 * clust_0) + \
                coeff[1] * (deg_1 + 2 * clust_1) + \
                coeff[2] * (deg_2 + 2 * clust_2) + \
                np.random.uniform(-5, 5)
            G.nodes[n]['favour'] = Y
        G_list.append(G)
    return G_list


# ---------------------------------------------------------------------------
# Helper: compute sorted indices with degree tie-breaking (mirrors the
# ranking logic inside approx_perm_rank_degree)
# ---------------------------------------------------------------------------

def compute_sorted_idx_rank_degree(nbh_list, dist_list):
    """Sort village indices by (distance to R, degree of matched NN within ties)."""
    dist_arr = np.array(dist_list)
    smallest_idx = np.argsort(dist_arr)

    dist_sort_set = np.sort(np.unique(dist_arr))
    dist_sort_num = np.array([np.sum(dist_arr == d) for d in dist_sort_set])

    sorted_idx = np.array([], dtype=int)
    start = 0
    for i in range(len(dist_sort_set)):
        end = int(np.sum(dist_sort_num[:i + 1]))
        temp = smallest_idx[start:end]
        temp_nbh = np.array(nbh_list)[temp]
        degree_list = [
            sum(dict(nbh.root_nbhd(2).network.degree()).values())
            for nbh in temp_nbh
        ]
        degree_rank = np.argsort(np.array(degree_list))
        temp = temp[degree_rank]
        sorted_idx = np.concatenate([sorted_idx, temp])
        start = end
    return sorted_idx.astype(int)


# ---------------------------------------------------------------------------
# Step 1: Load the Karnataka village data
# ---------------------------------------------------------------------------

filepath = DATA_DIR + "/"

print("Loading village data ...", flush=True)
t0 = timer()

G_list = []
for k in chain(range(1, 13), range(14, 22), range(23, 78)):
    with open(filepath + 'Adjacency Matrix Keys/key_HH_vilno_%d.csv' % k, 'r') as csv_file:
        lines = csv_file.readlines()
    vals = [int(v) for v in lines]
    key_dict = {i: vals[i] for i in range(len(vals))}

    G_visitgo   = nx.relabel_nodes(nx.Graph(pd.read_csv(filepath + 'Adjacency Matrices/adj_visitgo_HH_vilno_%d.csv'    % k, sep=",", quoting=csv.QUOTE_NONE, header=None).to_numpy()), key_dict)
    G_visitcome = nx.relabel_nodes(nx.Graph(pd.read_csv(filepath + 'Adjacency Matrices/adj_visitcome_HH_vilno_%d.csv'  % k, sep=",", quoting=csv.QUOTE_NONE, header=None).to_numpy()), key_dict)
    G_friends   = nx.relabel_nodes(nx.Graph(pd.read_csv(filepath + 'Adjacency Matrices/adj_nonrel_HH_vilno_%d.csv'     % k, sep=",", quoting=csv.QUOTE_NONE, header=None).to_numpy()), key_dict)
    G_lend      = nx.relabel_nodes(nx.Graph(pd.read_csv(filepath + 'Adjacency Matrices/adj_lendmoney_HH_vilno_%d.csv'  % k, sep=",", quoting=csv.QUOTE_NONE, header=None).to_numpy()), key_dict)
    G_borrow    = nx.relabel_nodes(nx.Graph(pd.read_csv(filepath + 'Adjacency Matrices/adj_borrowmoney_HH_vilno_%d.csv'% k, sep=",", quoting=csv.QUOTE_NONE, header=None).to_numpy()), key_dict)
    G_kercome   = nx.relabel_nodes(nx.Graph(pd.read_csv(filepath + 'Adjacency Matrices/adj_keroricecome_HH_vilno_%d.csv'% k, sep=",", quoting=csv.QUOTE_NONE, header=None).to_numpy()), key_dict)
    G_kergo     = nx.relabel_nodes(nx.Graph(pd.read_csv(filepath + 'Adjacency Matrices/adj_keroricego_HH_vilno_%d.csv' % k, sep=",", quoting=csv.QUOTE_NONE, header=None).to_numpy()), key_dict)

    G_favour  = nx.compose(nx.intersection(G_lend, G_borrow), nx.intersection(G_kercome, G_kergo))
    G_hedonic = nx.compose(nx.intersection(G_visitgo, G_visitcome), G_friends)
    G = G_hedonic

    for n in G.nodes:
        G.nodes[n]['favour'] = G_favour.degree(n)
    G.remove_nodes_from(list(nx.isolates(G)))
    G_list.append(G)

print(f"  Loaded {len(G_list)} villages in {timer()-t0:.1f}s", flush=True)

# ---------------------------------------------------------------------------
# Step 2: Build R1 (knife), R2 (fork), R3 (spoon) — same as original script
# ---------------------------------------------------------------------------

G_new = gen_data(1, 100, [0, 0, 0], seed=0)[0]
R1 = root_network(G_new.subgraph(9),  G_new)   # knife
R2 = root_network(G_new.subgraph(71), G_new)   # fork
R3 = root_network(G_new.subgraph(41), G_new)   # spoon

max_radius = 3   # same as in the paper's perm test calls

# ---------------------------------------------------------------------------
# Step 3: Cache find_NN distances + outcomes for all three configurations
# ---------------------------------------------------------------------------

def cache_config(R, G_list, max_radius, label):
    print(f"  Caching find_NN for {label} ...", flush=True)
    t0 = timer()
    nbh_list  = []
    dist_list = []
    for G in G_list:
        R_list = make_R_list_nodes(G)
        nbh, dist = find_NN(R, R_list, max_radius)
        nbh_list.append(nbh)
        dist_list.append(dist)
    f_list = np.array([x.favour for x in nbh_list])
    print(f"    done in {timer()-t0:.1f}s", flush=True)
    return nbh_list, dist_list, f_list


print("Caching find_NN results (expensive — ~5-10 min) ...", flush=True)
t_cache = timer()

nbh_knife,  dist_knife,  f_knife  = cache_config(R1.root_nbhd(2), G_list, max_radius, "knife (R1)")
nbh_fork,   dist_fork,   f_fork   = cache_config(R2.root_nbhd(2), G_list, max_radius, "fork  (R2)")
nbh_spoon,  dist_spoon,  f_spoon  = cache_config(R3.root_nbhd(2), G_list, max_radius, "spoon (R3)")

print(f"Total caching time: {timer()-t_cache:.1f}s", flush=True)

# Pre-compute sorted index arrays (distance-first, degree within ties)
sorted_knife = compute_sorted_idx_rank_degree(nbh_knife, dist_knife)
sorted_fork  = compute_sorted_idx_rank_degree(nbh_fork,  dist_fork)
sorted_spoon = compute_sorted_idx_rank_degree(nbh_spoon, dist_spoon)

n_villages = len(G_list)
print(f"  n = {n_villages} villages", flush=True)

# ---------------------------------------------------------------------------
# Step 4: Loop over q values, computing p-values
# ---------------------------------------------------------------------------
# Safe upper bound for q: zip_race needs at most 2q village slots from n villages.
# At iteration i (0-indexed), each index list has had at most i deletions, so
# requires n - i > i  =>  i < n/2.  With n=75: max i = 37, so max q = 37.
# We use q_values up to 35 to stay safely below this limit.

q_values = [1, 2, 3, 5, 8, 10, 15, 20, 25, 30, 35]
B = 999

# Single fixed seed before the loop for reproducibility
np.random.seed(42)
random.seed(42)

pvals_knife_fork = []
pvals_fork_spoon = []

print(f"\nRunning permutation tests (B={B}) for {len(q_values)} q values ...", flush=True)
t_loop = timer()

for q in q_values:
    t_q = timer()

    # --- knife = fork ---
    q_idx_kf1, q_idx_kf2 = zip_race(sorted_knife.copy(), sorted_fork.copy(), q)
    q_idx_kf1 = q_idx_kf1.astype(int)
    q_idx_kf2 = q_idx_kf2.astype(int)
    close_kf1 = f_knife[q_idx_kf1]
    close_kf2 = f_fork[q_idx_kf2]
    T_ref_kf  = CvM(close_kf1, close_kf2)
    total_kf  = np.concatenate((close_kf1, close_kf2))
    T_list_kf = np.zeros(B)
    for b in range(B):
        if b == 1:
            T_list_kf[b] = T_ref_kf
        else:
            perm = np.random.permutation(total_kf)
            T_list_kf[b] = CvM(perm[:q], perm[q:])
    p_kf = (1.0 / B) * np.sum(T_list_kf >= T_ref_kf)

    # --- fork = spoon ---
    q_idx_fs1, q_idx_fs2 = zip_race(sorted_fork.copy(), sorted_spoon.copy(), q)
    q_idx_fs1 = q_idx_fs1.astype(int)
    q_idx_fs2 = q_idx_fs2.astype(int)
    close_fs1 = f_fork[q_idx_fs1]
    close_fs2 = f_spoon[q_idx_fs2]
    T_ref_fs  = CvM(close_fs1, close_fs2)
    total_fs  = np.concatenate((close_fs1, close_fs2))
    T_list_fs = np.zeros(B)
    for b in range(B):
        if b == 1:
            T_list_fs[b] = T_ref_fs
        else:
            perm = np.random.permutation(total_fs)
            T_list_fs[b] = CvM(perm[:q], perm[q:])
    p_fs = (1.0 / B) * np.sum(T_list_fs >= T_ref_fs)

    pvals_knife_fork.append(float(p_kf))
    pvals_fork_spoon.append(float(p_fs))

    print(f"  q={q:2d}: p(knife=fork)={p_kf:.3f}  p(fork=spoon)={p_fs:.3f}  [{timer()-t_q:.1f}s]",
          flush=True)

print(f"Loop total: {timer()-t_loop:.1f}s", flush=True)

# ---------------------------------------------------------------------------
# Step 5: Output — table
# ---------------------------------------------------------------------------

table_path = os.path.join(OUT_DIR, 'extension_vary_q.txt')
with open(table_path, 'w') as f:
    f.write("Extension: p-values across q values (B=999 permutations, seed=42)\n")
    f.write("="*60 + "\n")
    f.write(f"{'q':>4}  {'p(knife=fork)':>14}  {'p(fork=spoon)':>14}  {'sig(fork=spoon)':>15}\n")
    f.write("-"*60 + "\n")
    for q, p_kf, p_fs in zip(q_values, pvals_knife_fork, pvals_fork_spoon):
        sig = "*" if p_fs < 0.05 else ""
        f.write(f"{q:>4}  {p_kf:>14.3f}  {p_fs:>14.3f}  {sig:>15}\n")
    f.write("-"*60 + "\n")
    f.write("Paper reports: q=5,10,20. * = reject H0 at alpha=0.05.\n")
    f.write("Paper's values (approx_perm_rank_degree, seed=19):\n")
    f.write("  q=5:  p(knife=fork)=0.597  p(fork=spoon)=0.157\n")
    f.write("  q=10: p(knife=fork)=0.432  p(fork=spoon)=0.007\n")
    f.write("  q=20: p(knife=fork)=0.432  p(fork=spoon)=0.074\n")

print(f"Table saved: {table_path}", flush=True)

# ---------------------------------------------------------------------------
# Step 6: Output — plot
# ---------------------------------------------------------------------------

fig, ax = plt.subplots(figsize=(8, 5))
ax.plot(q_values, pvals_knife_fork, 'b-o', markersize=6,
        label=r'$H_0: Y_\alpha =_d Y_\beta$ (knife $=$ fork)')
ax.plot(q_values, pvals_fork_spoon, 'r-s', markersize=6,
        label=r'$H_0: Y_\beta =_d Y_\gamma$ (fork $=$ spoon)')
ax.axhline(y=0.05, color='k', linestyle='--', linewidth=0.9,
           label=r'$\alpha = 0.05$')
ax.set_xlabel('$q$ (number of matched pairs)', fontsize=12)
ax.set_ylabel('$p$-value', fontsize=12)
ax.set_title('Permutation test $p$-values vs.\\ $q$\n(Karnataka villages, B=999)', fontsize=12)
ax.legend(fontsize=10)
ax.set_ylim(-0.02, 1.05)
ax.set_xticks(q_values)
plt.tight_layout()

plot_path = os.path.join(OUT_DIR, 'extension_vary_q.eps')
plt.savefig(plot_path, format='eps')
plt.close()
print(f"Plot  saved: {plot_path}", flush=True)

print("\nDone.", flush=True)

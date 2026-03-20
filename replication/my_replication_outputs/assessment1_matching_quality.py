#!/usr/bin/env python3
"""
Assessment 1 Diagnostic: Matching Quality (psi_g) Statistics
=============================================================
Quantifies the nearest-neighbor matching quality for knife, fork, and spoon
configurations against the 75 Karnataka village networks.

This script reproduces ONLY the distance-computation portion of
empirical-application.py (the section that generates Figure 12), then
adds numerical summaries not reported in the paper. No original code is
modified; all functions below are copied verbatim from empirical-application.py.

Run from: replication/my_replication_outputs/
  conda activate my-virtenv-py310
  python assessment1_matching_quality.py

Expected runtime: ~5-15 minutes (graph loading + 6 distance sweeps).
Output: assessment1_matching_quality.txt  (same directory)
"""

import numpy as np
import networkx as nx
import networkx.algorithms.isomorphism as iso
import random
import copy
import pandas as pd
import csv
from itertools import chain
from timeit import default_timer as timer
import os

# ---------------------------------------------------------------------------
# Path setup: script lives in my_replication_outputs/, data in ../Empirical-Application/
# ---------------------------------------------------------------------------
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR   = os.path.join(SCRIPT_DIR, '..', 'Empirical-Application') + os.sep
OUT_FILE   = os.path.join(SCRIPT_DIR, 'assessment1_matching_quality.txt')

# ---------------------------------------------------------------------------
# Functions copied verbatim from empirical-application.py
# (root_network, r_is_isomorphic, make_R_list_nodes, r_network_distance,
#  find_NN, gen_data)
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


def r_network_distance(R1, R2, max_radius, min_radius=0):
    R_10 = R1.root_nbhd(min_radius)
    R_20 = R2.root_nbhd(min_radius)
    if r_is_isomorphic(R_10, R_20) == False:
        return 1
    for d in range(min_radius + 1, max_radius + 2):
        if d == max_radius + 1:
            return 1/(d)
        else:
            R_1d = R1.root_nbhd(d)
            R_2d = R2.root_nbhd(d)
            if r_is_isomorphic(R_1d, R_2d) == False:
                return 1/(d)
            else:
                continue


def find_NN(R, R_list, max_radius):
    closest_nbh = R_list[0]
    closest_nbh_dist = r_network_distance(R, closest_nbh, max_radius)
    for R2 in R_list[1:]:
        if int(np.floor(1/closest_nbh_dist)) - 1 == max_radius:
            break
        else:
            dist = r_network_distance(R, R2, max_radius,
                                      int(np.floor(1/closest_nbh_dist)) - 1)
        if dist < closest_nbh_dist:
            closest_nbh = R2
            closest_nbh_dist = dist
    return closest_nbh, closest_nbh_dist


def gen_data(T, m, coeff=[0, 0, 0], seed=0):
    np.random.seed(seed)
    random.seed(seed)
    G_list = []
    for i in range(T):
        G = nx.erdos_renyi_graph(m, 2/m)
        for n in G.nodes:
             R = root_network(G.subgraph(n), G)
             G1 = R.root_nbhd(1).network
             G2 = R.root_nbhd(2).network
             G3 = R.root_nbhd(3).network
             clust_0 = nx.average_clustering(G1)
             clust_1 = nx.average_clustering(G2)
             clust_2 = nx.average_clustering(G3)
             deg_0 = sum(dict(G1.degree()).values())/len(G1)
             deg_1 = sum(dict(G2.degree()).values())/len(G2)
             deg_2 = sum(dict(G3.degree()).values())/len(G3)
             Y = coeff[0]*(deg_0 + 2*clust_0) + \
                 coeff[1]*(deg_1 + 2*clust_1) + \
                 coeff[2]*(deg_2 + 2*clust_2) + \
                 np.random.uniform(-5, 5)
             G.nodes[n]['favour'] = Y
        G_list.append(G)
    return G_list

# ---------------------------------------------------------------------------
# New diagnostic function (not in original script)
# ---------------------------------------------------------------------------

def compute_village_distances(target_R, G_list, max_radius):
    """
    For each village in G_list, find the nearest rooted network to target_R
    and return its distance.  Replicates the Figure 12 loop for a single target.
    """
    dists = []
    for G in G_list:
        R_list = make_R_list_nodes(G)
        _, d = find_NN(target_R, R_list, max_radius)
        dists.append(d)
    return np.array(dists)


def distance_summary(name, dists, max_radius, lines):
    """
    Print and record summary statistics for a distance array.
    `lines` is a list to append formatted strings to (for file output).
    """
    N = len(dists)
    perfect_dist = 1.0 / (max_radius + 1)          # best achievable distance
    unique_vals   = sorted(np.unique(dists))

    # Human-readable interpretation of each distance value
    def interp(dv, mr):
        if dv == 1.0 / (mr + 1):
            return f"perfect match (agrees through depth {mr})"
        elif dv == 1.0:
            return "differ at depth 0 or 1 (no structural overlap)"
        else:
            agree_depth = int(round(1.0/dv)) - 1
            return f"agrees through depth {agree_depth-1}, differs at depth {agree_depth}"

    header = f"\n  Configuration: {name.upper()}  (max_radius={max_radius})"
    lines.append(header)
    lines.append("  " + "-"*50)
    lines.append(f"  Number of villages: {N}")
    lines.append(f"  Perfect-match distance threshold: {perfect_dist:.4f}")

    lines.append(f"\n  Distance distribution:")
    for dv in unique_vals:
        cnt = int(np.sum(dists == dv))
        pct = 100.0 * cnt / N
        lines.append(f"    dist={dv:.4f}  {cnt:2d}/{N} villages ({pct:5.1f}%)  [{interp(dv, max_radius)}]")

    pct_exact = 100.0 * np.sum(dists == perfect_dist) / N
    lines.append(f"\n  % villages with perfect match : {pct_exact:.1f}%")
    lines.append(f"  Mean distance                 : {np.mean(dists):.4f}")
    lines.append(f"  Median distance               : {np.median(dists):.4f}")

    sorted_d = np.sort(dists)
    lines.append(f"\n  k-th nearest-neighbor distance (sorted best-first):")
    for k in [5, 10, 20, 30]:
        kd = sorted_d[k-1]
        lines.append(f"    k={k:2d}: dist={kd:.4f}  [{interp(kd, max_radius)}]")

    return {
        'pct_exact': pct_exact,
        'mean':      float(np.mean(dists)),
        'median':    float(np.median(dists)),
        'kth':       {k: float(sorted_d[k-1]) for k in [5, 10, 20, 30]},
        'dist_counts': {dv: int(np.sum(dists == dv)) for dv in unique_vals},
    }


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

total_start = timer()
lines = []   # accumulate all output lines

lines.append("=" * 70)
lines.append("ASSESSMENT 1: MATCHING QUALITY (psi_g) DIAGNOSTIC")
lines.append("Auerbach, Guo, Tabord-Meehan (2026) — Empirical Application")
lines.append("=" * 70)
lines.append(f"\nScript: assessment1_matching_quality.py")
lines.append(f"Purpose: Quantify nearest-neighbor match quality for knife,")
lines.append(f"         fork, and spoon configurations across 75 villages.")

# --- Load village graphs (identical to empirical-application.py lines 696-728) ---
lines.append("\n[1] Loading village graphs...")
print("[1] Loading village graphs...")
t0 = timer()

G_list = []
for k in chain(range(1, 13), range(14, 22), range(23, 78)):
    with open(DATA_DIR + 'Adjacency Matrix Keys/key_HH_vilno_%d.csv' % k, 'r') as csv_file:
        raw = csv_file.readlines()
    vals = [int(v) for v in raw]
    key_dict = {i: vals[i] for i in range(len(vals))}

    def load_adj(name):
        return nx.relabel_nodes(
            nx.Graph(pd.read_csv(DATA_DIR + f'Adjacency Matrices/{name}_HH_vilno_{k}.csv',
                                 sep=",", quoting=csv.QUOTE_NONE, header=None).to_numpy()),
            key_dict)

    G_visitgo   = load_adj('adj_visitgo')
    G_visitcome = load_adj('adj_visitcome')
    G_friends   = load_adj('adj_nonrel')
    G_lend      = load_adj('adj_lendmoney')
    G_borrow    = load_adj('adj_borrowmoney')
    G_kercome   = load_adj('adj_keroricecome')
    G_kergo     = load_adj('adj_keroricego')

    G_favour  = nx.compose(nx.intersection(G_lend, G_borrow),
                           nx.intersection(G_kercome, G_kergo))
    G_hedonic = nx.compose(nx.intersection(G_visitgo, G_visitcome), G_friends)
    G = G_hedonic
    for n in G.nodes:
        G.nodes[n]['favour'] = G_favour.degree(n)
    G.remove_nodes_from(list(nx.isolates(G)))
    G_list.append(G)

msg = f"    Loaded {len(G_list)} village graphs in {timer()-t0:.1f}s"
lines.append(msg); print(msg)

# Village size summary
sizes = [len(G.nodes) for G in G_list]
lines.append(f"    Village sizes: min={min(sizes)}, median={int(np.median(sizes))}, max={max(sizes)}")

# --- Generate target configurations (identical to lines 766-769) ---
lines.append("\n[2] Generating target configurations (seed=0, same as paper)...")
print("[2] Generating target configurations...")
G_new = gen_data(1, 100, [0, 0, 0], seed=0)[0]
R1 = root_network(G_new.subgraph(9),  G_new)   # knife (alpha)
R2 = root_network(G_new.subgraph(71), G_new)   # fork  (beta)
R3 = root_network(G_new.subgraph(41), G_new)   # spoon (gamma)
lines.append("    R1=knife (node 9), R2=fork (node 71), R3=spoon (node 41)")

# --- Compute distances ---
# max_radius=3: replicates Figure 12 exactly
# max_radius=2: matches the estimation setup (Table 2, EST_CI_ave uses max_radius=2)

results = {}

for mr, label in [(3, "Figure 12 setup (max_radius=3)"),
                  (2, "Table 2 estimation setup (max_radius=2)")]:
    lines.append(f"\n{'='*70}")
    lines.append(f"[3] Distance computation: {label}")
    lines.append(f"{'='*70}")
    print(f"\n[3] Computing distances ({label})...")

    for name, target in [('knife', R1), ('fork', R2), ('spoon', R3)]:
        print(f"    {name}...", end=' ', flush=True)
        t0 = timer()
        dists = compute_village_distances(target, G_list, max_radius=mr)
        elapsed = timer() - t0
        print(f"done ({elapsed:.1f}s)")
        results[(name, mr)] = distance_summary(name, dists, mr, lines)
        lines.append(f"    [runtime: {elapsed:.1f}s]")

# --- Comparison table ---
lines.append(f"\n{'='*70}")
lines.append("[4] COMPARISON TABLE — % villages with perfect match")
lines.append(f"{'='*70}")
lines.append(f"\n  {'Config':<8}  {'max_r=3 (Fig.12)':<22}  {'max_r=2 (Table 2 est.)'}")
lines.append("  " + "-"*60)
for name in ['knife', 'fork', 'spoon']:
    p3 = results[(name, 3)]['pct_exact']
    p2 = results[(name, 2)]['pct_exact']
    lines.append(f"  {name:<8}  {p3:5.1f}%{'':<17}  {p2:5.1f}%")

lines.append(f"\n{'='*70}")
lines.append("[5] COMPARISON TABLE — k-th nearest-neighbor distance")
lines.append(f"    (lower = better match; max_radius=2, Table 2 estimation context)")
lines.append(f"{'='*70}")
lines.append(f"\n  {'k':<6}  {'knife':>10}  {'fork':>10}  {'spoon':>10}")
lines.append("  " + "-"*45)
for k in [5, 10, 20, 30]:
    dk = results[('knife', 2)]['kth'][k]
    df = results[('fork',  2)]['kth'][k]
    ds = results[('spoon', 2)]['kth'][k]
    lines.append(f"  {k:<6}  {dk:>10.4f}  {df:>10.4f}  {ds:>10.4f}")

lines.append(f"\n  Note: distance=1/3 means agrees through depth 1 only (max_radius=2)")
lines.append(f"        distance=1/2 means agrees at depth 0 only")
lines.append(f"        distance=1   means no structural match even at depth 0 or 1")
lines.append(f"        distance=1/3 is the 'perfect match' threshold for max_radius=2")

lines.append(f"\n{'='*70}")
lines.append(f"Total runtime: {timer()-total_start:.1f}s")
lines.append(f"{'='*70}")

# --- Print and save ---
output = "\n".join(lines)
print("\n" + output)

with open(OUT_FILE, 'w') as f:
    f.write(output + "\n")

print(f"\nResults saved to: {OUT_FILE}")

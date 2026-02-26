import numpy as np
import networkx as nx
import networkx.algorithms.isomorphism as iso
import random
import copy

import numpy as np
# import networkx as nx
# import rooted_networks as rc
import pandas as pd
import csv
from itertools import chain
import matplotlib.pyplot as plt
import math # for factorial computation
# from sympy.utilities.iterables import multiset_permutations # for listing all permutations of a nparray

from timeit import default_timer as timer

class root_network(object):
    """The rooted network class.
    
    This class defines the features of a rooted network with potential node-level
    attributes. A rooted network is a network G with one distinguished node called
    the root.
    
    Attributes:
        network: A networkx graph object, which itself may have attributes (see notes below)
        root: A subnetwork of network which corresponds to the root (this is typically a node)
        takeup: (Optional) A binary variable which specifies whether or not the 
            root node took up microfinance.
    NOTES:
        The network object may itself have node-level attributes. These are 
        typically used for drawing and for checking whether two rooted networks
        are isomorphic:
            is_treat: (Optional) A binary variabile which specifies whether or 
                not a given node was informed about microfinance
            takeup: (Optional) A binary variable which specifies whether or 
                not a given node took up microfinance
            is_root: (Optional) A binary variable which specifies whether or 
                not a given node is part of the root.
            
    """
    def __init__(self, root, network):
        """Initalizes a rooted network object. """
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

        if 'meat_consump' in network.nodes[list(root.nodes)[0]]:
            self.meat_consump = network.nodes[list(root.nodes)[0]]['meat_consump']
        
    def root_nbhd(self, k):
        """Truncates a rooted network at a given distance k.
        Args:
            k: An integer which specifies the size of the neighbourhood. 
            A distance of k > 0 corresponds to the induced subgraph
                of the root with its neighbours within a path of lenght k.
        Returns:
            A rooted network object which corresponds to the truncated rooted 
                network.
        """
        node_list = []
        for node in list(self.root):
            node_list += nx.ego_graph(self.network, node, k).nodes
        sub_network = self.network.subgraph(node_list)
        return root_network(self.root, sub_network)
        
    def draw(self):
        """Draws a rooted network. The root is drawn as a diamond, the non-root
        nodes are drawn as circles. If the is_treat attribute is available, 
        the informed nodes are drawn in green, and the uninformed nodes are 
        drawn in red. Otherwise all nodes are drawn in blue.
        """
        pos = nx.spring_layout(self.network)
        # nx.draw_networkx_nodes(self.network, pos, nodelist = list(self.root), \
        #                  node_shape = 'd', with_labels = False, node_size = 100)
        
        # nx.draw_networkx_nodes(self.network, pos, nodelist = list(self.root), \
        #                  node_shape = 'd', node_size = 100)
        root_node = list(self.root)
        if self.network.nodes[root_node[0]]['treatment'] == 1:
            nx.draw_networkx_nodes(self.network, pos, nodelist = root_node, \
                         node_shape = 'd', node_size = 100, node_color = 'red')
        else:
            nx.draw_networkx_nodes(self.network, pos, nodelist = root_node, \
                         node_shape = 'd', node_size = 100)
            
        # nx.draw_networkx_nodes(self.network, pos, \
        #                  nodelist = [x for x in list(self.network) if x not in list(self.root)], \
        #                  node_shape = 'o', with_labels = False, node_size = 100)
        
        # nx.draw_networkx_nodes(self.network, pos, \
        #                  nodelist = [x for x in list(self.network) if x not in list(self.root)], \
        #                  node_shape = 'o', node_size = 100)
        nx.draw_networkx_nodes(self.network, pos, \
                         nodelist = [x for x in list(self.network) if x not in list(self.root) and self.network.nodes[x]['treatment'] == 1], \
                         node_shape = 'o', node_size = 100, node_color = 'red')
        nx.draw_networkx_nodes(self.network, pos, \
                         nodelist = [x for x in list(self.network) if x not in list(self.root) and self.network.nodes[x]['treatment'] == 0], \
                         node_shape = 'o', node_size = 100)
        

        nx.draw_networkx_edges(self.network, pos, edgelist = list(self.root.edges),
                               style = 'dashed')
        nx.draw_networkx_edges(self.network, pos, \
                               edgelist = [e for e in list(self.network.edges) \
                                           if e not in self.root.edges])

        
        # [x for x in list(self.network) if x not in list(self.root) and ]


def r_is_isomorphic_epsilon1(R1, R2):
    """Determines if two rooted networks are isomorphic. (epsilon=1: don't care about attribute)
    
    Args:
        R1: A rooted network
        R2: A rooted network
        
    Returns: A boolean which corresponds to if the two rooted networks are 
    isomorphic.
    
    NOTES: If the is_treat attribute is available, this will also be used to
    determine if the networks are isomorphic.
    """
    G1 = R1.network
    G2 = R2.network
    if nx.faster_could_be_isomorphic(G1, G2) == False:
        return False
    else:
        # nm = iso.categorical_node_match('is_root', 0)
        nm = iso.categorical_node_match('is_root', 0)
        nm_edge = iso.categorical_edge_match('is_root', 0)
        return nx.is_isomorphic(G1, G2, node_match = nm, edge_match = nm_edge)

def r_is_isomorphic_epsilon0(R1, R2):
    """Determines if two rooted networks are isomorphic. (epsilon=0: care about attribute)
    
    Args:
        R1: A rooted network
        R2: A rooted network
        
    Returns: A boolean which corresponds to if the two rooted networks are 
    isomorphic.
    
    NOTES: If the is_treat attribute is available, this will also be used to
    determine if the networks are isomorphic.
    """
    G1 = R1.network
    G2 = R2.network
    if nx.faster_could_be_isomorphic(G1, G2) == False:
        return False
    else:
        # nm = iso.categorical_node_match('is_root', 0)
        nm = iso.categorical_node_match(['is_root', 'treatment'], [0, 0])
        nm_edge = iso.categorical_edge_match('is_root', 0)
        return nx.is_isomorphic(G1, G2, node_match = nm, edge_match = nm_edge)
    
def make_R_list_nodes(G):
    """This function takes in a network and returns a list of the rooted networks rooted at each node"""
    R_list = []
    for n in G.nodes:
        R = root_network(G.subgraph(n), G)
        R_list.append(R)
    return R_list

def r_network_distance_epsilon1(R1, R2, max_radius, min_radius = 0):
    """This function takes in two rooted networks and returns their distance (epsilon = 1: assuming 'treatment' don't match)"""
    R_10 = R1.root_nbhd(min_radius)
    R_20 = R2.root_nbhd(min_radius)
    if r_is_isomorphic_epsilon1(R_10, R_20) == False:
        return 1 + 1 
    for d in range(min_radius + 1, max_radius + 2):
        if d == max_radius + 1:
            return 1/(d) + 1
        else:
            R_1d = R1.root_nbhd(d)
            R_2d = R2.root_nbhd(d)
            if r_is_isomorphic_epsilon1(R_1d, R_2d) == False:
                return 1/(d) + 1
            else:
                continue
                
def r_network_distance_epsilon0(R1, R2, max_radius, min_radius = 0):
    """This function takes in two rooted networks and returns their distance (epsilon = 0: need to account for 'treatment' match)"""
    R_10 = R1.root_nbhd(min_radius)
    R_20 = R2.root_nbhd(min_radius)
    if r_is_isomorphic_epsilon0(R_10, R_20) == False:
        return 2 #this may not be the true network distance but good enough for our purposes
    for d in range(min_radius + 1, max_radius + 2):
        if d == max_radius + 1:
            return 1/(d) 
        else:
            R_1d = R1.root_nbhd(d)
            R_2d = R2.root_nbhd(d)
            if r_is_isomorphic_epsilon0(R_1d, R_2d) == False:
                return 1/(d) 
            else:
                continue

def r_network_distance(R1, R2, max_radius, min_radius = 0):
    """This function takes in two rooted networks and returns their distance (node-level)"""
    return min(r_network_distance_epsilon1(R1, R2, max_radius, min_radius), r_network_distance_epsilon0(R1, R2, max_radius, min_radius))
            
# def ASF_hat(R, G_list, max_radius, k): 
#     """This returns an estimate of the average structural function of the rooted network R given a list of networks G_list"""
#     """(tie-breaking)"""
#     nbh_list = []
#     dist_list = []
#     for G in G_list:
#         R_list = make_R_list_nodes(G)
#         closest_nbh, closest_nbh_dist = find_NN(R, R_list, max_radius)
#         nbh_list.append(closest_nbh) 
#         dist_list.append(closest_nbh_dist)      
#     # favour_nbh_list = np.array([x.favour for x in nbh_list])
#     meat_consump_nbh_list = np.array([x.meat_consump for x in nbh_list])
#     avg = np.zeros(len(k))
#     for idx, nn in enumerate(k):
#         smallest_idx = np.argsort(np.array(dist_list)) 
#         # final_nbh = favour_nbh_list[smallest_idx[:nn]]
#         final_nbh = meat_consump_nbh_list[smallest_idx[:nn]]
#         avg[idx] = np.mean(final_nbh)
#         nbh_list_sort = np.array(nbh_list)[smallest_idx[:nn]]
#     return avg, sorted(dist_list), nbh_list_sort

    

def make_psi(dist_list):
    domain = np.arange(0, 1.01, 0.01)
    psi = np.zeros(len(domain))
    N = len(dist_list)
    for idx, d in enumerate(domain):
        psi[idx] = sum(k <= d for k in dist_list)/N
    return psi
    
def upper_inverse(function_domain, function_values):
    inverse_function_values = []
    l = len(function_values)
    for a in function_domain:
        for idx, val in enumerate(function_values):
            if idx == l - 1:
                inverse_function_values.append(max(function_domain))
            else:
                if val <= a and function_values[idx + 1] > a:
                    inverse_function_values.append(function_domain[idx])
                    break
                else:
                    continue
    return inverse_function_values

def F_hat(data, x):
    q = len(data)
    return (1/q)*sum(1*(d <= x) for d in data)

def CvM(data1, data2):
    """This function returns the Cramer von-Mises distance between two empirical CDFs, it's used for the hypothesis test"""
    q = len(data1)
    return (1/(2*q))*sum((F_hat(data1, x) - F_hat(data2, x))**2 for x in np.concatenate((data1, data2)))
        
def approx_perm(R1, R2, G_list, max_radius, q, test_level = 0, B = 999):
    """This function performs the approximate permutation test given two rooted networks and a list of networks to draw the
    nearest neighbors from.
    """
    nbh_list1 = []
    nbh_list2 = []
    dist_list1 = []
    dist_list2 = []
    #print(len(G_list))
    i = 0
    for G in G_list:
        #print(i)
        R_list = make_R_list_nodes(G)
        closest_nbh, closest_nbh_dist = find_NN(R1, R_list, max_radius)
        nbh_list1.append(closest_nbh)
        dist_list1.append(closest_nbh_dist) 
        closest_nbh, closest_nbh_dist = find_NN(R2, R_list, max_radius)
        nbh_list2.append(closest_nbh)
        dist_list2.append(closest_nbh_dist) 
        i = i+1
    f_list1 = np.array([x.favour for x in nbh_list1])
    f_list2 = np.array([x.favour for x in nbh_list2])
    smallest_idx1 = np.argsort(np.array(dist_list1))
    smallest_idx2 = np.argsort(np.array(dist_list2))
    q_idx1, q_idx2 = zip_race(smallest_idx1, smallest_idx2, q)
    close_list1 = f_list1[q_idx1]
    close_list2 = f_list2[q_idx2]
    T_reference = CvM(close_list1, close_list2)
    T_list = np.zeros(B)
    close_total = np.concatenate((close_list1, close_list2))
    for b in range(B):
        if b == 1:
            T_list[b] = T_reference
        else:
            close_permute = np.random.permutation(close_total)
            cp1 = close_permute[:q]
            cp2 = close_permute[q:]
            T_list[b] = CvM(cp1, cp2)  
            #print(T_list[b])
    #print(T_reference)
    #print(close_list1,close_list2)
    if test_level == 0:               
        return (1/B)*sum(1*(t >= T_reference) for t in T_list), np.array(dist_list1)[q_idx1], np.array(dist_list2)[q_idx2], list(np.array(nbh_list1)[q_idx1]), list(np.array(nbh_list2)[q_idx2]) 
    else:
        T_list.sort()
        M = len(T_list)
        k = int(M - np.ceil(M*test_level))
        M_plus = sum(1*(t > T_list[k]) for t in T_list)
        M_0 = sum(1*(t == T_list[k]) for t in T_list)
        a = (M*test_level - M_plus)/M_0
        if T_reference > T_list[k]:
            return 1, np.array(dist_list1)[q_idx1], np.array(dist_list2)[q_idx2], list(np.array(nbh_list1)[q_idx1]), list(np.array(nbh_list2)[q_idx2])  
        elif T_reference == T_list[k]:
            return np.random.binomial(1, a, 1)[0], np.array(dist_list1)[q_idx1], np.array(dist_list2)[q_idx2], list(np.array(nbh_list1)[q_idx1]), list(np.array(nbh_list2)[q_idx2]) 
        else:
            return 0, np.array(dist_list1)[q_idx1], np.array(dist_list2)[q_idx2], list(np.array(nbh_list1)[q_idx1]), list(np.array(nbh_list2)[q_idx2])  





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
    """Find the nearest neighbor of a given rooted network R given a list of rooted networks R_list, THIS IS WHERE TIE-BREAKING
    MIGHT BE A PROBLEM"""
    closest_nbh = R_list[0]
    closest_nbh_dist = r_network_distance(R, closest_nbh, max_radius)
    for R2 in R_list[1:]:
        if int(np.floor(1/closest_nbh_dist)) - 1 == max_radius:
            # do not need to use np.floor? because 1/closest_nbh_dist should be an integer by definition?
            break
        else:
            dist = r_network_distance(R, R2, max_radius, \
                                      int(np.floor(1/closest_nbh_dist)) - 1) 
            # if there is another R_list[k] having the same distance to R as R_list[0], then choose R_list[0]
        if dist < closest_nbh_dist:
            closest_nbh = R2
            closest_nbh_dist = dist
    return closest_nbh, closest_nbh_dist
    

def gen_data_node_level_treatment_WS(T, m, coeff = [0, 0, 0, 0, 0, 0], seed = 0):
    np.random.seed(seed)
    random.seed(seed)
    G_list = []
    for i in range(T):
        G = nx.watts_strogatz_graph(m, 2, 0.3)
        for n in G.nodes:
            G.nodes[n]['treatment'] = np.random.binomial(n=1, p=0.25)
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

            treatment_root = G.nodes[n]['treatment']
            
            treatments_G1 = []
            for n_1 in G1.nodes:
                treatments_G1.append(G1.nodes[n_1]['treatment'])
            treatment_rd1 = np.sum(treatments_G1) - treatment_root

            treatments_G2 = []
            for n_2 in G2.nodes:
                treatments_G2.append(G2.nodes[n_2]['treatment'])
            treatment_rd2 = np.sum(treatments_G2) - treatment_rd1 - treatment_root
            
            Y = coeff[0]*(deg_0 + 2*clust_0) + \
                coeff[1]*(deg_1 + 2*clust_1) + \
                coeff[2]*(deg_2 + 2*clust_2) + \
                coeff[3]*treatment_root + \
                coeff[4]*treatment_rd1 + \
                coeff[5]*treatment_rd2 + \
                np.random.uniform(-4, 4)
            G.nodes[n]['favour'] = Y
        G_list.append(G)
    return G_list

def run_hyp_node_level_treatment(T, m, coeff, q, g_num_1, g_num_2, itera = 1000):
    
    start = timer()
    
    print("T:", T, " m:", m)
    
    if 2*q > T:
        q == int(T/2)

    # Generate the target networks
    G_list = gen_data_node_level_treatment_WS(20, 50, coeff, seed = 0)

    G0 = G_list[0]
    R0_list = make_R_list_nodes(G0)
    g2 = R0_list[31].root_nbhd(2)
    g3 = R0_list[26].root_nbhd(2)
    g4 = R0_list[11].root_nbhd(2)
    g5 = R0_list[45].root_nbhd(2)
    g7 = R0_list[14].root_nbhd(2)
    g8 = R0_list[42].root_nbhd(2)
    
    G1 = G_list[1]
    R1_list = make_R_list_nodes(G1)
    g1 = R1_list[34].root_nbhd(2)
    
    G5 = G_list[5]
    R5_list = make_R_list_nodes(G5)
    g6 = R5_list[27].root_nbhd(2)

    g_set = [g1,g2,g3,g4,g5,g6,g7,g8]
    g_names = ["g1","g2","g3","g4","g5","g6","g7","g8"]

    graph_1 = g_set[(g_num_1-1)]
    graph_2 = g_set[(g_num_2-1)]

    # Testing
    rej_rate1 = 0

    graph_1_prop_exact_match = np.zeros(itera)
    graph_1_prop_rd1_match = np.zeros(itera)
    graph_1_prop_rd0_match = np.zeros(itera)
    graph_2_prop_exact_match = np.zeros(itera)
    graph_2_prop_rd1_match = np.zeros(itera)
    graph_2_prop_rd0_match = np.zeros(itera)
    for i in range(itera):
        G_list = gen_data_node_level_treatment_WS(T, m, coeff, seed = i+1)

        # graph_1 vs graph_2
        p1, dist_list12_1, dist_list12_2, nbh_list12_1, nbh_list12_2 = approx_perm(graph_1, graph_2, G_list, 2, q, test_level = 0.05)
        rej_rate1 += p1
        graph_1_prop_exact_match[i] = np.mean(dist_list12_1<1/2)
        graph_1_prop_rd1_match[i] = np.mean(dist_list12_1<1) - np.mean(dist_list12_1<1/2)
        graph_1_prop_rd0_match[i] = np.mean(dist_list12_1==1)
        graph_2_prop_exact_match[i] = np.mean(dist_list12_2<1/2)
        graph_2_prop_rd1_match[i] = np.mean(dist_list12_2<1) - np.mean(dist_list12_2<1/2)
        graph_2_prop_rd0_match[i] = np.mean(dist_list12_2==1)
    end = timer()

    with open(f"tiebreaking_C{T}_q{q}_coeff{coeff[3]}{coeff[4]}{coeff[5]}_WS_g{g_num_1}{g_num_2}.txt", 'w') as my_output:
        # my_output.write("g_3 =_d g_4: %f \n g_1 =_d g_2: %f \n" % (rej_rate1/itera, rej_rate2/itera))
        # my_output.write("proportion of matches (g3, 1/3,1/2,1): %f, %f, %f \n" % (np.mean(g3_prop_exact_match), np.mean(g3_prop_rd1_match), np.mean(g3_prop_rd0_match)))
        # my_output.write("proportion of matches (g4, 1/3,1/2,1): %f, %f, %f \n" % (np.mean(g4_prop_exact_match), np.mean(g4_prop_rd1_match), np.mean(g4_prop_rd0_match)))
        # my_output.write("proportion of matches (g1, 1/3,1/2,1): %f, %f, %f \n" % (np.mean(g1_prop_exact_match), np.mean(g1_prop_rd1_match), np.mean(g1_prop_rd0_match)))
        # my_output.write("proportion of matches (g2, 1/3,1/2,1): %f, %f, %f \n" % (np.mean(g2_prop_exact_match), np.mean(g2_prop_rd1_match), np.mean(g2_prop_rd0_match)))
        # my_output.write("Running time: %f \n" % (end - start))
        my_output.write(g_names[(g_num_1-1)]+" =_d "+g_names[(g_num_2-1)]+": %f \n" % (rej_rate1/itera))
        my_output.write("proportion of matches ("+g_names[(g_num_1-1)]+", 1/3,1/2,1): %f, %f, %f \n" % (np.mean(graph_1_prop_exact_match), np.mean(graph_1_prop_rd1_match), np.mean(graph_1_prop_rd0_match)))
        my_output.write("proportion of matches ("+g_names[(g_num_2-1)]+", 1/3,1/2,1): %f, %f, %f \n" % (np.mean(graph_2_prop_exact_match), np.mean(graph_2_prop_rd1_match), np.mean(graph_2_prop_rd0_match)))
        my_output.write("Running time: %f \n" % (end - start))

    
    
    print(f"H_0: tilde g_{g_num_1} =_d tilde g_{g_num_2} (Watts-Strogatz(2,0.3), U in [-4,4], theta=(0,2,0,{coeff[3]},{coeff[4]},{coeff[5]})), C={T}, q={q}: {float(rej_rate1/itera)*100:.1f}")
    # print("Running time:", end - start)
    with open(f"partial_replication_results.txt", 'a') as my_output:
            my_output.write(f"H_0: tilde g_{g_num_1} =_d tilde g_{g_num_2} (Watts-Strogatz(2,0.3), U in [-4,4], theta=(0,2,0,{coeff[3]},{coeff[4]},{coeff[5]})), C={T}, q={q}: {float(rej_rate1/itera)*100:.1f} \n")
    # print("proportion of matches ("+g_names[(g_num_1-1)]+", 1/3,1/2,1): %f, %f, %f \n" % (np.mean(graph_1_prop_exact_match), np.mean(graph_1_prop_rd1_match), np.mean(graph_1_prop_rd0_match)))
    # print("proportion of matches ("+g_names[(g_num_2-1)]+", 1/3,1/2,1): %f, %f, %f \n" % (np.mean(graph_2_prop_exact_match), np.mean(graph_2_prop_rd1_match), np.mean(graph_2_prop_rd0_match)))



import argparse
def parse_commandline():
    """Parse the arguments given on the command-line.
    """
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-argument-1",
                       help="Input argument 1")
    parser.add_argument("--input-argument-2",
                       help="Input argument 2")
    parser.add_argument("--input-argument-3",
                       help="Input argument 3")
    parser.add_argument("--input-argument-4",
                       help="Input argument 4")
    parser.add_argument("--input-argument-5",
                       help="Input argument 5")
    parser.add_argument("--input-argument-6",
                       help="Input argument 6")
    parser.add_argument("--input-argument-7",
                       help="Input argument 7")
    parser.add_argument("--input-argument-8",
                       help="Input argument 8")

    args = parser.parse_args()

    return args

if __name__ == '__main__':
    args = parse_commandline()
    
T = int(args.input_argument_1)
m = 20
q = int(args.input_argument_2)
coeff = [0, 2, 0, int(args.input_argument_3), int(args.input_argument_4), int(args.input_argument_5)]
g_num_1 = int(args.input_argument_6)
g_num_2 = int(args.input_argument_7)
itera = int(args.input_argument_8)

run_hyp_node_level_treatment(T, m, coeff, q, g_num_1, g_num_2, itera)



import numpy as np
import networkx as nx
import networkx.algorithms.isomorphism as iso
import random
import copy
import pandas as pd
import csv
from itertools import chain
import matplotlib.pyplot as plt
from timeit import default_timer as timer
from decimal import Decimal
import scipy.stats as st
import igraph as ig
import os

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
        nx.draw_networkx_nodes(self.network, pos, nodelist = list(self.root), \
                         node_shape = 'd', node_size = 100)
        # nx.draw_networkx_nodes(self.network, pos, \
        #                  nodelist = [x for x in list(self.network) if x not in list(self.root)], \
        #                  node_shape = 'o', with_labels = False, node_size = 100)
        nx.draw_networkx_nodes(self.network, pos, \
                         nodelist = [x for x in list(self.network) if x not in list(self.root)], \
                         node_shape = 'o', node_size = 100)
        nx.draw_networkx_edges(self.network, pos, edgelist = list(self.root.edges),
                               style = 'dashed')
        nx.draw_networkx_edges(self.network, pos, \
                               edgelist = [e for e in list(self.network.edges) \
                                           if e not in self.root.edges])

    def draw_igraph(self, ax):
        """Draws a rooted network. The root is drawn as a diamond, the non-root
        nodes are drawn as circles. If the is_treat attribute is available, 
        the informed nodes are drawn in green, and the uninformed nodes are 
        drawn in red. Otherwise all nodes are drawn in blue.
        """
        
        g = ig.Graph.from_networkx(self.network)
        g_1 = ig.Graph.from_networkx(self.root_nbhd(1).network)

        # fig, ax = plt.subplots()
        # layout = g.layout_reingold_tilford()
        # layout = g.layout("sphere")
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

def r_is_isomorphic(R1, R2):
    """Determines if two rooted networks are isomorphic. 
    
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
        nm = iso.categorical_node_match('is_root', 0)
        nm_edge = iso.categorical_edge_match('is_root', 0)
        return nx.is_isomorphic(G1, G2, node_match = nm, edge_match = nm_edge)
    
def make_R_list_nodes(G):
    """This function takes in a network and returns a list of the rooted networks rooted at each node"""
    R_list = []
    for n in G.nodes:
        R = root_network(G.subgraph(n), G)
        R_list.append(R)
    return R_list

def r_network_distance(R1, R2, max_radius, min_radius = 0):
    """This function takes in two rooted networks and returns their distance"""
    R_10 = R1.root_nbhd(min_radius)
    R_20 = R2.root_nbhd(min_radius)
    if r_is_isomorphic(R_10, R_20) == False:
        return 1 #this may not be the true network distance but good enough for our purposes
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
            
def ASF_hat(R, G_list, max_radius, k): 
    """This returns an estimate of the average structural function of the rooted network R given a list of networks G_list"""
    nbh_list = []
    dist_list = []
    for G in G_list:
        R_list = make_R_list_nodes(G)
        closest_nbh, closest_nbh_dist = find_NN(R, R_list, max_radius)
        nbh_list.append(closest_nbh)
        dist_list.append(closest_nbh_dist)      
    favour_nbh_list = np.array([x.favour for x in nbh_list])
    avg = np.zeros(len(k))
    for idx, nn in enumerate(k):
        smallest_idx = np.argsort(np.array(dist_list)) 
        final_nbh = favour_nbh_list[smallest_idx[:nn]]
        avg[idx] = np.mean(final_nbh)
        if nn==k[idx]:
            nbh_list_sort = np.array(nbh_list)[smallest_idx[:nn]]
    return avg, dist_list, nbh_list_sort

def ASF_hat_ave(R, G_list, max_radius, k): 
    """This returns an estimate of the average structural function of the rooted network R given a list of networks G_list"""

    """
    Averaging
    """
    nbh_list = []
    dist_list = []
    for G in G_list:
        R_list = make_R_list_nodes(G)
        closest_nbh, closest_nbh_dist = find_NN_ave(R, R_list, max_radius)
        nbh_list.append(closest_nbh)
        dist_list.append(closest_nbh_dist)
    nbh_num_list = [len(nbh_list[i]) for i in range(len(nbh_list))]
    favour_nbh_list = []
    for i in range(len(nbh_list)):
        favour_nbh_list.append(np.mean([nbh_list[i][l].favour for l in range(len(nbh_list[i]))]))
    favour_nbh_list = np.array(favour_nbh_list)
    avg = np.zeros(len(k))
    nbh_num_nn_list = []
    dist_nn_list = []
    for idx, nn in enumerate(k):
        smallest_idx = np.argsort(np.array(dist_list)) 
        nbh_num_nn_list.append(np.array(nbh_num_list)[smallest_idx[:nn]].tolist())
        dist_nn_list.append(np.array(dist_list)[smallest_idx[:nn]].tolist())
        final_nbh = favour_nbh_list[smallest_idx[:nn]]
        avg[idx] = np.mean(final_nbh)
    return avg, dist_nn_list, nbh_num_nn_list
    
"""I think these functions are for drawing density curves, you can ignore them for now"""
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
""""""""""""

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

def approx_perm_rank_degree(R1, R2, G_list, max_radius, q, test_level = 0, B = 999):
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
    # np.random.seed(shuffle_seed)
    # random.seed(shuffle_seed)
    
    dist1_sort_set = np.sort(np.unique(np.array(dist_list1)))   
    dist2_sort_set = np.sort(np.unique(np.array(dist_list2)))
    dist1_sort_num = []
    dist2_sort_num = []
    for i in range(len(dist1_sort_set)):
        dist1_sort_num.append(np.sum(np.array(dist_list1)==dist1_sort_set[i]))
    for i in range(len(dist2_sort_set)):
        dist2_sort_num.append(np.sum(np.array(dist_list2)==dist2_sort_set[i]))
    dist1_sort_num = np.array(dist1_sort_num)
    dist2_sort_num = np.array(dist2_sort_num)
    
    smallest_idx1_rank_degree = np.array([])
    smallest_idx2_rank_degree = np.array([])
    start = 0
    for i in range(len(dist1_sort_set)):
        end = np.sum(dist1_sort_num[0:i+1])
        temp = smallest_idx1[start:end]
        temp_nbh = np.array(nbh_list1)[temp]
        degree_list = []
        for j in range(len(temp_nbh)):
            degree_list.append(sum(dict(temp_nbh[j].root_nbhd(2).network.degree()).values()) )
        degree_rank = np.argsort(np.array(degree_list))
        temp = temp[degree_rank]
        smallest_idx1_rank_degree = np.concatenate([smallest_idx1_rank_degree, temp])
        start = end
    start = 0
    for i in range(len(dist2_sort_set)):
        end = np.sum(dist2_sort_num[0:i+1])
        temp = smallest_idx2[start:end]
        temp_nbh = np.array(nbh_list2)[temp]
        degree_list = []
        for j in range(len(temp_nbh)):
            degree_list.append(sum(dict(temp_nbh[j].root_nbhd(2).network.degree()).values()) )
        degree_rank = np.argsort(np.array(degree_list))
        temp = temp[degree_rank]
        smallest_idx2_rank_degree = np.concatenate([smallest_idx2_rank_degree, temp])
        start = end
    
    q_idx1, q_idx2 = zip_race(smallest_idx1_rank_degree, smallest_idx2_rank_degree, q)
    q_idx1 = q_idx1.astype(int)
    q_idx2 = q_idx2.astype(int)
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

def approx_perm_shuffle(R1, R2, G_list, max_radius, q, shuffle_seed, test_level = 0, B = 999):
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
    np.random.seed(shuffle_seed)
    random.seed(shuffle_seed)
    
    dist1_sort_set = np.sort(np.unique(np.array(dist_list1)))   
    dist2_sort_set = np.sort(np.unique(np.array(dist_list2)))
    dist1_sort_num = []
    dist2_sort_num = []
    for i in range(len(dist1_sort_set)):
        dist1_sort_num.append(np.sum(np.array(dist_list1)==dist1_sort_set[i]))
    for i in range(len(dist2_sort_set)):
        dist2_sort_num.append(np.sum(np.array(dist_list2)==dist2_sort_set[i]))
    dist1_sort_num = np.array(dist1_sort_num)
    dist2_sort_num = np.array(dist2_sort_num)
    
    smallest_idx1_shuffle = np.array([])
    smallest_idx2_shuffle = np.array([])
    start = 0
    for i in range(len(dist1_sort_set)):
        end = np.sum(dist1_sort_num[0:i+1])
        temp = smallest_idx1[start:end]
        np.random.shuffle(temp)
        smallest_idx1_shuffle = np.concatenate([smallest_idx1_shuffle, temp])
        start = end
    start = 0
    for i in range(len(dist2_sort_set)):
        end = np.sum(dist2_sort_num[0:i+1])
        temp = smallest_idx2[start:end]
        np.random.shuffle(temp)
        smallest_idx2_shuffle = np.concatenate([smallest_idx2_shuffle, temp])
        start = end
    
    q_idx1, q_idx2 = zip_race(smallest_idx1_shuffle, smallest_idx2_shuffle, q)
    q_idx1 = q_idx1.astype(int)
    q_idx2 = q_idx2.astype(int)
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

def EST_CI_ave(R1, R2, G_list, max_radius, k, alpha): 
    """This returns an estimate of the average structural function of the rooted network R given a list of networks G_list"""

    """
    Estimation of E[h(R1)-h(R2)] by averaging and report CI
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
        closest_nbh, closest_nbh_dist = find_NN_ave(R1, R_list, max_radius)
        nbh_list1.append(closest_nbh)
        dist_list1.append(closest_nbh_dist) 
        closest_nbh, closest_nbh_dist = find_NN_ave(R2, R_list, max_radius)
        nbh_list2.append(closest_nbh)
        dist_list2.append(closest_nbh_dist) 
        i = i+1
        
    f_list1 = []
    for i in range(len(nbh_list1)):
        f_list1.append(np.mean([nbh_list1[i][l].favour for l in range(len(nbh_list1[i]))]))
    f_list1 = np.array(f_list1)
    
    f_list2 = []
    for i in range(len(nbh_list2)):
        f_list2.append(np.mean([nbh_list2[i][l].favour for l in range(len(nbh_list2[i]))]))
    f_list2 = np.array(f_list2)
    # f_list1 = np.array([x.favour for x in nbh_list1])
    # f_list2 = np.array([x.favour for x in nbh_list2])
    smallest_idx1 = np.argsort(np.array(dist_list1))
    smallest_idx2 = np.argsort(np.array(dist_list2))
    k_idx1, k_idx2 = zip_race(smallest_idx1, smallest_idx2, k)
    close_list1 = f_list1[k_idx1]
    close_list2 = f_list2[k_idx2]

    h1 = np.mean(close_list1)
    h2 = np.mean(close_list2)
    var1 = np.var(close_list1, ddof=0)
    var2 = np.var(close_list2, ddof=0)

    est = h1 - h2
    ci_lb = est - st.norm.ppf(1-alpha/2) * np.sqrt((var1+var2)/k)
    ci_ub = est - st.norm.ppf(alpha/2) * np.sqrt((var1+var2)/k)

    # dist_nn_list1 = np.array(dist_list1)[k_idx1]
    # dist_nn_list2 = np.array(dist_list2)[k_idx2]
    return est, ci_lb, ci_ub # , dist_nn_list1, dist_nn_list2
    # return avg, dist_nn_list, nbh_num_nn_list

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

def find_NN_ave(R, R_list, max_radius):
    """
    Now finding all rooted networks with the closest distance
    """
    dist = []
    for R2 in R_list:
        dist.append(r_network_distance(R, R2, max_radius))
    closest_nbh_dist = min(dist)
    dist_arr = np.array(dist)
    closest_nbh = np.array(R_list)[dist_arr == closest_nbh_dist].tolist()
    return closest_nbh, closest_nbh_dist

def gen_data(T, m, coeff = [0, 0, 0], seed = 0):
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
             Y = coeff[0]*(deg_0 + 2*clust_0) +\
                 coeff[1]*(deg_1 + 2*clust_1) + \
                 coeff[2]*(deg_2 + 2*clust_2) + \
                 np.random.uniform(-5, 5)
             G.nodes[n]['favour'] = Y
        G_list.append(G)
    return G_list

# def compute_mean(R, coeff = [0, 0 ,0]):
#     G1 = R.root_nbhd(1).network
#     G2 = R.root_nbhd(2).network
#     G3 = R.root_nbhd(3).network
#     clust_0 = nx.average_clustering(G1)
#     clust_1 = nx.average_clustering(G2)
#     clust_2 = nx.average_clustering(G3)
#     deg_0 = sum(dict(G1.degree()).values())/len(G1)
#     deg_1 = sum(dict(G2.degree()).values())/len(G2)
#     deg_2 = sum(dict(G3.degree()).values())/len(G3)
#     m = coeff[0]*(deg_0 + 2*clust_0) +\
#                  coeff[1]*(deg_1 + 2*clust_1) + \
#                  coeff[2]*(deg_2 + 2*clust_2) 
#     return m


def plot_ecdfs(datasets, network_names, fig_file_name):
    # Create a figure with subplots for each dataset
    fig, axes = plt.subplots(1, len(datasets), figsize=(15, 5), sharey=True)
    
    for i, data in enumerate(datasets):
        # Sort data in ascending order
        data = np.sort(data)
        
        # Calculate ECDF values
        n = len(data)
        y = np.arange(1, n + 1) / n
        
        # Extend data to cover values beyond the min and max
        extended_data = np.concatenate(([0], data, [1]))
        extended_y = np.concatenate(([0], y, [1]))
        
        # Plot ECDF as a step function in the corresponding subplot
        axes[i].step(extended_data, extended_y, where='post')
        axes[i].set_xlabel('distance')
        axes[i].set_title(network_names[i])
        axes[i].set_xlim(0, 1)
        # Remove the grid
        axes[i].grid(False)
    
    # Set common y-axis label
    axes[0].set_ylabel(r'$\psi_g(x)$')
    # plt.suptitle(r'Estimated $\psi_g(\cdot)$ for knife, fork, and spoon')
    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    plt.savefig(fig_file_name, format="eps")
    # plt.show()

# Rounding results
def rounding_2dec(number):
    return str(Decimal(number).quantize(Decimal("0.01"), rounding = "ROUND_HALF_UP"))

def rounding_3dec(number):
    return str(Decimal(number).quantize(Decimal("0.001"), rounding = "ROUND_HALF_UP"))

"""This is the code to load in the graphs"""
filepath = os.getcwd() + "/"

start = timer()

G_list = []
for k in chain(range(1, 13), range(14, 22), range(23, 78)):
    with open(filepath + 'Adjacency Matrix Keys/key_HH_vilno_%d.csv' %k,'r') as csv_file:
        lines = csv_file.readlines()
    vals = [int(v) for v in lines]
    key_dict = {i: vals[i] for i in range(len(vals))}
    
    G_visitgo = nx.relabel_nodes(nx.Graph(pd.read_csv(filepath + 'Adjacency Matrices/adj_visitgo_HH_vilno_%d.csv' %k, \
                             sep=",", quoting=csv.QUOTE_NONE, header = None).to_numpy()), key_dict)
    G_visitcome = nx.relabel_nodes(nx.Graph(pd.read_csv(filepath + 'Adjacency Matrices/adj_visitcome_HH_vilno_%d.csv' %k, \
                             sep=",", quoting=csv.QUOTE_NONE, header = None).to_numpy()), key_dict)
    G_friends = nx.relabel_nodes(nx.Graph(pd.read_csv(filepath + 'Adjacency Matrices/adj_nonrel_HH_vilno_%d.csv' %k, \
                         sep=",", quoting=csv.QUOTE_NONE, header = None).to_numpy()), key_dict)
    
    G_lend = nx.relabel_nodes(nx.Graph(pd.read_csv(filepath + 'Adjacency Matrices/adj_lendmoney_HH_vilno_%d.csv' %k, \
                             sep=",", quoting=csv.QUOTE_NONE, header = None).to_numpy()), key_dict)
    G_borrow = nx.relabel_nodes(nx.Graph(pd.read_csv(filepath + 'Adjacency Matrices/adj_borrowmoney_HH_vilno_%d.csv' %k, \
                               sep=",", quoting=csv.QUOTE_NONE, header = None).to_numpy()), key_dict)
    G_kercome = nx.relabel_nodes(nx.Graph(pd.read_csv(filepath + 'Adjacency Matrices/adj_keroricecome_HH_vilno_%d.csv' %k, \
                                sep=",", quoting=csv.QUOTE_NONE, header = None).to_numpy()), key_dict)
    G_kergo = nx.relabel_nodes(nx.Graph(pd.read_csv(filepath + 'Adjacency Matrices/adj_keroricego_HH_vilno_%d.csv' %k, \
                              sep=",", quoting=csv.QUOTE_NONE, header = None).to_numpy()), key_dict)
    G_favour = nx.compose(nx.intersection(G_lend, G_borrow), nx.intersection(G_kercome, G_kergo))
    
    G_hedonic = nx.compose(nx.intersection(G_visitgo, G_visitcome), G_friends)  
    G = G_hedonic
    
    
    for n in G.nodes:
        G.nodes[n]['favour'] = G_favour.degree(n)

    G.remove_nodes_from(list(nx.isolates(G)))
    G_list.append(G)



# Summary statistics (Table 1)
num_hh_village = np.zeros(len(G_list))
for i in range(len(G_list)):
    num_hh_village[i] = len(G_list[i].nodes)

num_hh = str(Decimal(np.sum(num_hh_village)).quantize(Decimal("0"), rounding = "ROUND_HALF_UP"))
mean_hh_per_village = str(Decimal(np.mean(num_hh_village)).quantize(Decimal("0"), rounding = "ROUND_HALF_UP"))
min_num_hh = str(Decimal(np.min(num_hh_village)).quantize(Decimal("0"), rounding = "ROUND_HALF_UP"))
quantile_25 = str(Decimal(np.quantile(num_hh_village, 0.25)).quantize(Decimal("0"), rounding = "ROUND_HALF_UP"))
quantile_50 = str(Decimal(np.quantile(num_hh_village, 0.5)).quantize(Decimal("0"), rounding = "ROUND_HALF_UP"))
quantile_75 = str(Decimal(np.quantile(num_hh_village, 0.75)).quantize(Decimal("0"), rounding = "ROUND_HALF_UP"))
max_num_hh = str(Decimal(np.max(num_hh_village)).quantize(Decimal("0"), rounding = "ROUND_HALF_UP"))

# Table 1 (txt output)
with open(f"Table1.txt", 'w') as my_output:
    my_output.write(r"\begin{table}[htbp]" + "\n")
    my_output.write(r"\centering" + "\n")
    my_output.write(r"\caption{Summary statistics for the number of households per village}" + "\n")
    my_output.write(r"\begin{tabular}{cccccccc}" + "\n")
    my_output.write(r"\toprule" + "\n")
    my_output.write(r"Total Num. & Mean  & Min & 25\% Quantile & 50\% Quantile & 75\% Quantile & Max \\" + "\n")
    my_output.write(r"\midrule" + "\n")
    my_output.write(num_hh + "&" + mean_hh_per_village + "&" + min_num_hh + "&" + quantile_25 + "&" + quantile_50 + "&" + quantile_75 + "&" + max_num_hh + r"\\" + "\n")
    my_output.write(r"\bottomrule" + "\n")
    my_output.write(r"\end{tabular}" + "\n")
    my_output.write(r"\label{tab:summary_stats_app}" + "\n")
    my_output.write(r"\end{table}")

"""This was a lazy way to generate the fork/spoon/knife etc subgraphs by first generating a graph with a given seed and then
extracting the right subgraphs. SHOULD CHECK THAT THIS PRODUCES THE RIGHT SUBGRAPHS ON YOUR MACHINE."""
# G_new = rc.gen_data(1, 100, [0,0,0], seed = 0)[0]
# R1 = rc.root_network(G_new.subgraph(9), G_new)   
# R2 = rc.root_network(G_new.subgraph(71), G_new)  
# R3 = rc.root_network(G_new.subgraph(41), G_new)    
G_new = gen_data(1, 100, [0,0,0], seed = 0)[0]
R1 = root_network(G_new.subgraph(9), G_new)   
R2 = root_network(G_new.subgraph(71), G_new)  
R3 = root_network(G_new.subgraph(41), G_new)   
# R1.root_nbhd(2).draw()
# plt.show()
# R2.root_nbhd(2).draw()
# plt.show()
# R3.root_nbhd(2).draw()
# plt.show()

# Testing (ranking by degree), q = 20
np.random.seed(19)
random.seed(19)

q = 20

start = timer()
p1_q20_r, dist_list12_1_q20_r, dist_list12_2_q20_r, nbh_list12_1_q20_r, nbh_list12_2_q20_r = approx_perm_rank_degree(R1.root_nbhd(2), R2.root_nbhd(2), G_list, 3, q)
p2_q20_r, dist_list23_2_q20_r, dist_list23_3_q20_r, nbh_list23_2_q20_r, nbh_list23_3_q20_r = approx_perm_rank_degree(R2.root_nbhd(2), R3.root_nbhd(2), G_list, 3, q)
end = timer()
print("running time (q=20):", end - start)
print("p-values (knife v.s. fork, q=20):", p1_q20_r)
print("p-values (fork v.s. spoon, q=20):", p2_q20_r)

# Testing (ranking by degree), q = 10
np.random.seed(19)
random.seed(19)

q = 10

start = timer()
p1_q10_r, dist_list12_1_q10_r, dist_list12_2_q10_r, nbh_list12_1_q10_r, nbh_list12_2_q10_r = approx_perm_rank_degree(R1.root_nbhd(2), R2.root_nbhd(2), G_list, 3, q)
p2_q10_r, dist_list23_2_q10_r, dist_list23_3_q10_r, nbh_list23_2_q10_r, nbh_list23_3_q10_r = approx_perm_rank_degree(R2.root_nbhd(2), R3.root_nbhd(2), G_list, 3, q)
end = timer()
print("running time (q=10):", end - start)
print("p-values (knife v.s. fork, q=10):", p1_q10_r)
print("p-values (fork v.s. spoon, q=10):", p2_q10_r)

# Testing (ranking by degree), q = 5
np.random.seed(19)
random.seed(19)

q = 5

start = timer()
p1_q5_r, dist_list12_1_q5_r, dist_list12_2_q5_r, nbh_list12_1_q5_r, nbh_list12_2_q5_r = approx_perm_rank_degree(R1.root_nbhd(2), R2.root_nbhd(2), G_list, 3, q)
p2_q5_r, dist_list23_2_q5_r, dist_list23_3_q5_r, nbh_list23_2_q5_r, nbh_list23_3_q5_r = approx_perm_rank_degree(R2.root_nbhd(2), R3.root_nbhd(2), G_list, 3, q)
end = timer()
print("running time (q=5):", end - start)
print("p-values (knife v.s. fork, q=5):", p1_q5_r)
print("p-values (fork v.s. spoon, q=5):", p2_q5_r)

# p-values for empirical application

p1_q5_r_str = rounding_3dec(p1_q5_r)
p1_q10_r_str = rounding_3dec(p1_q10_r)
p1_q20_r_str = rounding_3dec(p1_q20_r)
p2_q5_r_str = rounding_3dec(p2_q5_r)
p2_q10_r_str = rounding_3dec(p2_q10_r)
p2_q20_r_str = rounding_3dec(p2_q20_r)

with open(f"p-values-empirical-applicaiton.txt", 'w') as my_output:
    my_output.write(r"Y_\alpha =_d Y_\beta (p-values for q=5,10,20): " + f"{p1_q5_r_str}, {p1_q10_r_str}, {p1_q20_r_str}" + "\n")
    my_output.write(r"Y_\beta =_d Y_\gamma (p-values for q=5,10,20): " + f"{p2_q5_r_str}, {p2_q10_r_str}, {p2_q20_r_str}" + "\n")

# Plot the rooted networks (radius = 2) used for testing
# Figures 8-11

nbh_list_sort = [nbh_list12_1_q20_r, nbh_list12_2_q20_r, nbh_list23_2_q20_r, nbh_list23_3_q20_r]
fig_titles = ["Rooted Networks (radius=2) used for approximating Knife in testing of Fork vs Knife",
             "Rooted Networks (radius=2) used for approximating Fork in testing of Fork vs Knife ",
             "Rooted Networks (radius=2) used for approximating Fork in testing of Spoon vs Fork",
             "Rooted Networks (radius=2) used for approximating Spoon in testing of Spoon vs Fork"]
# fig_file_names = ["closest_knife_forkvsknife_jackson_testing_rank_degree.eps", 
#                  "closest_fork_forkvsknife_jackson_testing_rank_degree.eps",
#                  "closest_fork_spoonvsfork_jackson_testing_rank_degree.eps",
#                  "closest_spoon_spoonvsfork_jackson_testing_rank_degree.eps"]
fig_file_names = ["Figure8.eps", 
                 "Figure9.eps",
                 "Figure10.eps",
                 "Figure11.eps"]

for fig_num in range(len(nbh_list_sort)):

    nbh_list = nbh_list_sort[fig_num]
    fig_title = fig_titles[fig_num]
    fig_file_name = fig_file_names[fig_num]
    
    # Define the grid size
    num_elements = len(nbh_list)
    num_cols = 5  # Choose the number of columns you want (adjust as needed)
    num_rows = 4  # Calculate rows needed
    
    # Set up the plot
    fig, axes = plt.subplots(num_rows, num_cols, figsize=(15, 10))
    # fig.suptitle(fig_title, fontsize=16)
    
    # Flatten axes array for easier iteration (in case of uneven rows/columns)
    axes = axes.flatten()
    
    # Draw each element in the list on a separate subplot
    for i in range(num_elements):
        # Set the current subplot as the active one
        plt.sca(axes[i])
        nbh_list[i].root_nbhd(2).draw_igraph(axes[i])  # Draw the network
    
    # Hide any remaining subplots if `nbh_list_sort1` has fewer elements than the grid
    for j in range(i + 1, len(axes)):
        axes[j].axis('off')
    
    plt.tight_layout(rect=[0, 0.03, 1, 0.95])  # Adjust layout to fit titles and spacing
    plt.savefig(fig_file_name, format="eps")
    # plt.show()

# Estimation and CIs: knife v.s. fork, k=10

max_radius = 2
k = 10
alpha = 0.05

np.random.seed(19)
random.seed(19)

fork_knife_est_k10, ci95_fork_knife_lb_k10, ci95_fork_knife_ub_k10 = EST_CI_ave(R2, R1, G_list, max_radius, k, alpha)
spoon_fork_est_k10, ci95_spoon_fork_lb_k10, ci95_spoon_fork_ub_k10 = EST_CI_ave(R3, R2, G_list, max_radius, k, alpha)
print("Treatment effect (knife v.s. fork, k=10):", fork_knife_est_k10)
print("95% CI (knife v.s. fork, k=10):", [ci95_fork_knife_lb_k10, ci95_fork_knife_ub_k10])
print("Treatment effect (fork v.s. spoon, k=10):", spoon_fork_est_k10)
print("95% CI (fork v.s. spoon, k=10):", [ci95_spoon_fork_lb_k10, ci95_spoon_fork_ub_k10])

# Estimation and CIs: fork v.s. spoon, k=10

max_radius = 2
k = 10
alpha = 0.1

np.random.seed(19)
random.seed(19)

fork_knife_est_k10, ci90_fork_knife_lb_k10, ci90_fork_knife_ub_k10 = EST_CI_ave(R2, R1, G_list, max_radius, k, alpha)
spoon_fork_est_k10, ci90_spoon_fork_lb_k10, ci90_spoon_fork_ub_k10 = EST_CI_ave(R3, R2, G_list, max_radius, k, alpha)
print("Treatment effect (knife v.s. fork, k=10):", fork_knife_est_k10)
print("90% CI (knife v.s. fork, k=10):", [ci90_fork_knife_lb_k10, ci90_fork_knife_ub_k10])
print("Treatment effect (fork v.s. spoon, k=10):", spoon_fork_est_k10)
print("90% CI (fork v.s. spoon, k=10):", [ci90_spoon_fork_lb_k10, ci90_spoon_fork_ub_k10])

# Estimation and CIs: knife v.s. fork, k=20

max_radius = 2
k = 20
alpha = 0.05

np.random.seed(19)
random.seed(19)

fork_knife_est_k20, ci95_fork_knife_lb_k20, ci95_fork_knife_ub_k20 = EST_CI_ave(R2, R1, G_list, max_radius, k, alpha)
spoon_fork_est_k20, ci95_spoon_fork_lb_k20, ci95_spoon_fork_ub_k20 = EST_CI_ave(R3, R2, G_list, max_radius, k, alpha)
print("Treatment effect (knife v.s. fork, k=20):", fork_knife_est_k20)
print("95% CI (knife v.s. fork, k=20):", [ci95_fork_knife_lb_k20, ci95_fork_knife_ub_k20])
print("Treatment effect (fork v.s. spoon, k=20):", spoon_fork_est_k20)
print("95% CI (fork v.s. spoon, k=20):", [ci95_spoon_fork_lb_k20, ci95_spoon_fork_ub_k20])

# Estimation and CIs: fork v.s. spoon, k=20

max_radius = 2
k = 20
alpha = 0.1

np.random.seed(19)
random.seed(19)

fork_knife_est_k20, ci90_fork_knife_lb_k20, ci90_fork_knife_ub_k20 = EST_CI_ave(R2, R1, G_list, max_radius, k, alpha)
spoon_fork_est_k20, ci90_spoon_fork_lb_k20, ci90_spoon_fork_ub_k20 = EST_CI_ave(R3, R2, G_list, max_radius, k, alpha)
print("Treatment effect (knife v.s. fork, k=20):", fork_knife_est_k20)
print("90% CI (knife v.s. fork, k=20):", [ci90_fork_knife_lb_k20, ci90_fork_knife_ub_k20])
print("Treatment effect (fork v.s. spoon, k=20):", spoon_fork_est_k20)
print("90% CI (fork v.s. spoon, k=20):", [ci90_spoon_fork_lb_k20, ci90_spoon_fork_ub_k20])

# Estimation and CIs: knife v.s. fork, k=30

max_radius = 2
k = 30
alpha = 0.05

np.random.seed(19)
random.seed(19)

fork_knife_est_k30, ci95_fork_knife_lb_k30, ci95_fork_knife_ub_k30 = EST_CI_ave(R2, R1, G_list, max_radius, k, alpha)
spoon_fork_est_k30, ci95_spoon_fork_lb_k30, ci95_spoon_fork_ub_k30 = EST_CI_ave(R3, R2, G_list, max_radius, k, alpha)
print("Treatment effect (knife v.s. fork, k=30):", fork_knife_est_k30)
print("95% CI (knife v.s. fork, k=30):", [ci95_fork_knife_lb_k30, ci95_fork_knife_ub_k30])
print("Treatment effect (fork v.s. spoon, k=30):", spoon_fork_est_k30)
print("95% CI (fork v.s. spoon, k=30):", [ci95_spoon_fork_lb_k30, ci95_spoon_fork_ub_k30])

# Estimation and CIs: fork v.s. spoon, k=30

max_radius = 2
k = 30
alpha = 0.1

np.random.seed(19)
random.seed(19)

fork_knife_est_k30, ci90_fork_knife_lb_k30, ci90_fork_knife_ub_k30 = EST_CI_ave(R2, R1, G_list, max_radius, k, alpha)
spoon_fork_est_k30, ci90_spoon_fork_lb_k30, ci90_spoon_fork_ub_k30 = EST_CI_ave(R3, R2, G_list, max_radius, k, alpha)
print("Treatment effect (knife v.s. fork, k=30):", fork_knife_est_k30)
print("90% CI (knife v.s. fork, k=30):", [ci90_fork_knife_lb_k30, ci90_fork_knife_ub_k30])
print("Treatment effect (fork v.s. spoon, k=30):", spoon_fork_est_k30)
print("90% CI (fork v.s. spoon, k=30):", [ci90_spoon_fork_lb_k30, ci90_spoon_fork_ub_k30])

# Table 2 (Estimates and confidence intervals of treatment effects, txt output)
with open(f"Table2.txt", 'w') as my_output:
    my_output.write(r"\begin{table}[htbp]" + "\n")
    my_output.write(r"\centering" + "\n")
    my_output.write(r"\caption{Estimates and confidence intervals of treatment effects}" + "\n")
    my_output.write(r"\begin{tabular}{cccc}" + "\n")
    my_output.write(r"\toprule" + "\n")
    my_output.write(r"& & $ E[Y_\beta] -  E[Y_\alpha]$ & $ E[Y_\gamma] - E[Y_\beta]$\\" + "\n")
    my_output.write(r"\midrule" + "\n")
    my_output.write(r"\multirow{3}{*}{$k=10$} & Est.&" +f"{rounding_2dec(fork_knife_est_k10)} & {rounding_2dec(spoon_fork_est_k10)}" + r"\\"  + "\n")
    my_output.write(r"& 95\% CI&" + f"[{rounding_2dec(ci95_fork_knife_lb_k10)},{rounding_2dec(ci95_fork_knife_ub_k10)}] & [{rounding_2dec(ci95_spoon_fork_lb_k10)},{rounding_2dec(ci95_spoon_fork_ub_k10)}]" + r"\\" + "\n")
    my_output.write(r"& 90\% CI&" + f"[{rounding_2dec(ci90_fork_knife_lb_k10)},{rounding_2dec(ci90_fork_knife_ub_k10)}] & [{rounding_2dec(ci90_spoon_fork_lb_k10)},{rounding_2dec(ci90_spoon_fork_ub_k10)}]" + r"\\" + "\n")
    my_output.write(r"\midrule" + "\n")
    my_output.write(r"\multirow{3}{*}{$k=20$} &Est. &" + f"{rounding_2dec(fork_knife_est_k20)}& {rounding_2dec(spoon_fork_est_k20)}" + r"\\" + "\n")
    my_output.write(r"& 95\% CI&" + f"[{rounding_2dec(ci95_fork_knife_lb_k20)},{rounding_2dec(ci95_fork_knife_ub_k20)}] & [{rounding_2dec(ci95_spoon_fork_lb_k20)},{rounding_2dec(ci95_spoon_fork_ub_k20)}]" + r"\\" + "\n")
    my_output.write(r"& 90\% CI&" + f"[{rounding_2dec(ci90_fork_knife_lb_k20)},{rounding_2dec(ci90_fork_knife_ub_k20)}] & [{rounding_2dec(ci90_spoon_fork_lb_k20)},{rounding_2dec(ci90_spoon_fork_ub_k20)}]" + r"\\" + "\n")
    my_output.write(r"\midrule" + "\n")
    my_output.write(r"\multirow{3}{*}{$k=30$} &Est. &" + f"{rounding_2dec(fork_knife_est_k30)}& {rounding_2dec(spoon_fork_est_k30)}" + r"\\" + "\n")
    my_output.write(r"& 95\% CI&" + f"[{rounding_2dec(ci95_fork_knife_lb_k30)},{rounding_2dec(ci95_fork_knife_ub_k30)}] & [{rounding_2dec(ci95_spoon_fork_lb_k30)},{rounding_2dec(ci95_spoon_fork_ub_k30)}]" + r"\\" + "\n")
    my_output.write(r"& 90\% CI&" + f"[{rounding_2dec(ci90_fork_knife_lb_k30)},{rounding_2dec(ci90_fork_knife_ub_k30)}] & [{rounding_2dec(ci90_spoon_fork_lb_k30)},{rounding_2dec(ci90_spoon_fork_ub_k30)}]" + r"\\" + "\n")
    my_output.write(r"\bottomrule" + "\n")
    my_output.write(r"\end{tabular}" + "\n")
    my_output.write(r"\label{tab:est_ci}" + "\n")
    my_output.write(r"\end{table}")

# Robust check for testing (q = 5)

q = 5
shuffle_seed_set = [1,2,3,4,5,6,7,8,9,10]

p1_set_q5 = []
p2_set_q5 = []
for i in range(len(shuffle_seed_set)):
    shuffle_seed = shuffle_seed_set[i]
    p1_q5, dist_list12_1_q5, dist_list12_2_q5, nbh_list12_1_q5, nbh_list12_2_q5 = approx_perm_shuffle(R1.root_nbhd(2), R2.root_nbhd(2), G_list, 3, q, shuffle_seed)
    p2_q5, dist_list23_2_q5, dist_list23_3_q5, nbh_list23_2_q5, nbh_list23_3_q5 = approx_perm_shuffle(R2.root_nbhd(2), R3.root_nbhd(2), G_list, 3, q, shuffle_seed)
    p1_set_q5.append(p1_q5)
    p2_set_q5.append(p2_q5)

print(p1_set_q5)
print(p2_set_q5)

# Robust check for testing (q = 10)

q = 10
shuffle_seed_set = [1,2,3,4,5,6,7,8,9,10]

p1_set_q10 = []
p2_set_q10 = []
for i in range(len(shuffle_seed_set)):
    shuffle_seed = shuffle_seed_set[i]
    p1_q10, dist_list12_1_q10, dist_list12_2_q10, nbh_list12_1_q10, nbh_list12_2_q10 = approx_perm_shuffle(R1.root_nbhd(2), R2.root_nbhd(2), G_list, 3, q, shuffle_seed)
    p2_q10, dist_list23_2_q10, dist_list23_3_q10, nbh_list23_2_q10, nbh_list23_3_q10 = approx_perm_shuffle(R2.root_nbhd(2), R3.root_nbhd(2), G_list, 3, q, shuffle_seed)
    p1_set_q10.append(p1_q10)
    p2_set_q10.append(p2_q10)

print(p1_set_q10)
print(p2_set_q10)

# Robust check for testing (q = 20)

q = 20
shuffle_seed_set = [1,2,3,4,5,6,7,8,9,10]

p1_set_q20 = []
p2_set_q20 = []
for i in range(len(shuffle_seed_set)):
    shuffle_seed = shuffle_seed_set[i]
    p1_q20, dist_list12_1_q20, dist_list12_2_q20, nbh_list12_1_q20, nbh_list12_2_q20 = approx_perm_shuffle(R1.root_nbhd(2), R2.root_nbhd(2), G_list, 3, q, shuffle_seed)
    p2_q20, dist_list23_2_q20, dist_list23_3_q20, nbh_list23_2_q20, nbh_list23_3_q20 = approx_perm_shuffle(R2.root_nbhd(2), R3.root_nbhd(2), G_list, 3, q, shuffle_seed)
    p1_set_q20.append(p1_q20)
    p2_set_q20.append(p2_q20)

print(p1_set_q20)
print(p2_set_q20)

p1_set_q5_str = ""
p1_set_q10_str = ""
p1_set_q20_str = ""
p2_set_q5_str = ""
p2_set_q10_str = ""
p2_set_q20_str = ""
for i in range(len(p1_set_q5)):
    p1_set_q5_str += r"&" + f"{rounding_2dec(p1_set_q5[i])}"
    p1_set_q10_str += r"&" + f"{rounding_2dec(p1_set_q10[i])}"
    p1_set_q20_str += r"&" + f"{rounding_2dec(p1_set_q20[i])}"
    p2_set_q5_str += r"&" + f"{rounding_2dec(p2_set_q5[i])}"
    p2_set_q10_str += r"&" + f"{rounding_2dec(p2_set_q10[i])}"
    p2_set_q20_str += r"&" + f"{rounding_2dec(p2_set_q20[i])}"

# Table 12 (txt output)
with open(f"Table12.txt", 'w') as my_output:
    my_output.write(r"\begin{table}[htbp]" + "\n")
    my_output.write(r"\centering" + "\n")
    my_output.write(r"\caption{$p$-values for testing $Y_\alpha =_d Y_\beta$ among 10 different random picks of rooted networks with the same distance to the target rooted network}" + "\n")
    my_output.write(r"\begin{tabular}{ccccccccccc}" + "\n")
    my_output.write(r"\toprule" + "\n")
    my_output.write(r"$q=5$" + p1_set_q5_str + r"\\" + "\n")
    my_output.write(r"$q=10$" + p1_set_q10_str + r"\\" + "\n")
    my_output.write(r"$q=20$" + p1_set_q20_str + r"\\" + "\n")
    my_output.write(r"\bottomrule" + "\n")
    my_output.write(r"\end{tabular}" + "\n")
    my_output.write(r"\label{tab:robust_p_knife_fork}" + "\n")
    my_output.write(r"\end{table}")

# Table 13 (txt output)
with open(f"Table13.txt", 'w') as my_output:
    my_output.write(r"\begin{table}[htbp]" + "\n")
    my_output.write(r"\centering" + "\n")
    my_output.write(r" \caption{$p$-values for testing $Y_\beta =_d Y_\gamma$ among 10 different random picks of rooted networks with the same distance to the target rooted network}" + "\n")
    my_output.write(r"\begin{tabular}{ccccccccccc}" + "\n")
    my_output.write(r"\toprule" + "\n")
    my_output.write(r"$q=5$" + p2_set_q5_str + r"\\" + "\n")
    my_output.write(r"$q=10$" + p2_set_q10_str + r"\\" + "\n")
    my_output.write(r"$q=20$" + p2_set_q20_str + r"\\" + "\n")
    my_output.write(r"\bottomrule" + "\n")
    my_output.write(r"\end{tabular}" + "\n")
    my_output.write(r"\label{tab:robust_p_fork_spoon}" + "\n")
    my_output.write(r"\end{table}")

# Estimated \psi_g
# Figure 12

max_radius = 3
dist_knife_list = []
dist_fork_list = []
dist_spoon_list = []
for G in G_list:
    R_list = make_R_list_nodes(G)
    closest_nbh_knife, closest_nbh_knife_dist = find_NN(R1, R_list, max_radius)
    closest_nbh_fork, closest_nbh_fork_dist = find_NN(R2, R_list, max_radius)
    closest_nbh_spoon, closest_nbh_spoon_dist = find_NN(R3, R_list, max_radius)
    dist_knife_list.append(closest_nbh_knife_dist)
    dist_fork_list.append(closest_nbh_fork_dist)
    dist_spoon_list.append(closest_nbh_spoon_dist)

dist_knife_list_new = []
dist_fork_list_new = []
dist_spoon_list_new = []

for i in range(len(G_list)):
    if dist_knife_list[i] <= 1/4:
        dist_knife_list_new.append(0)
    else:
        dist_knife_list_new.append(dist_knife_list[i])

    if dist_fork_list[i] <= 1/4:
        dist_fork_list_new.append(0)
    else:
        dist_fork_list_new.append(dist_fork_list[i])

    if dist_spoon_list[i] <= 1/4:
        dist_spoon_list_new.append(0)
    else:
        dist_spoon_list_new.append(dist_spoon_list[i])

datasets = [dist_knife_list_new, dist_fork_list_new, dist_spoon_list_new]
network_names = ['knife', 'fork', 'spoon']
# fig_file_name = 'EDF_distance.eps'
fig_file_name = 'Figure12.eps'
plot_ecdfs(datasets, network_names, fig_file_name)

end = timer()
print("elapsed time:", end - start)



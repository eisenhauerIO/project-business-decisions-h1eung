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

def compute_mean(R, coeff = [0, 0 ,0]):
    G1 = R.root_nbhd(1).network
    G2 = R.root_nbhd(2).network
    G3 = R.root_nbhd(3).network
    clust_0 = nx.average_clustering(G1)
    clust_1 = nx.average_clustering(G2)
    clust_2 = nx.average_clustering(G3)
    deg_0 = sum(dict(G1.degree()).values())/len(G1)
    deg_1 = sum(dict(G2.degree()).values())/len(G2)
    deg_2 = sum(dict(G3.degree()).values())/len(G3)
    m = coeff[0]*(deg_0 + 2*clust_0) +\
                 coeff[1]*(deg_1 + 2*clust_1) + \
                 coeff[2]*(deg_2 + 2*clust_2) 
    return m


def plot_ecdfs_fig6(datasets, network_names, fig_file_name):
    # Create a figure with subplots for each dataset
    fig, axes = plt.subplots(1, len(datasets), figsize=(10, 5), sharey=True)
    
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

def gen_data_WS_2_02(T, m, coeff = [0, 0, 0], seed = 0):
    np.random.seed(seed)
    random.seed(seed)
    G_list = []
    for i in range(T):
        # G = nx.erdos_renyi_graph(m, 2/m)
        # G = nx.random_geometric_graph(m, 0.2)
        G = nx.watts_strogatz_graph(m, 2, 0.2)
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

def gen_data_WS_2_08(T, m, coeff = [0, 0, 0], seed = 0):
    np.random.seed(seed)
    random.seed(seed)
    G_list = []
    for i in range(T):
        # G = nx.erdos_renyi_graph(m, 2/m)
        # G = nx.random_geometric_graph(m, 0.2)
        G = nx.watts_strogatz_graph(m, 2, 0.8)
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

def gen_data_WS_2_0275(T, m, coeff = [0, 0, 0], seed = 0):
    np.random.seed(seed)
    random.seed(seed)
    G_list = []
    for i in range(T):
        # G = nx.erdos_renyi_graph(m, 2/m)
        # G = nx.random_geometric_graph(m, 0.2)
        G = nx.watts_strogatz_graph(m, 2, 0.275)
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

def gen_data_RG(T, m, coeff = [0, 0, 0], seed = 0):
    np.random.seed(seed)
    random.seed(seed)
    G_list = []
    for i in range(T):
        # G = nx.erdos_renyi_graph(m, 2/m)
        G = nx.random_geometric_graph(m, 0.2)
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

start = timer()

coeff = [0, 2, 0]

G_new = gen_data(1, 100, coeff, seed = 0)[0]

G_new2 = G_new.copy()
G_new3 = G_new.copy()
G_new2.add_edge(71, 4)
G_new2.add_node(200)
G_new2.add_edge(17,200)
G_new3.add_edge(4, 20)
G_new3.add_node(200)
G_new3.add_edge(17,200)
R1 = root_network(G_new2.subgraph(71), G_new2)
R2 = root_network(G_new3.subgraph(71), G_new3)

m1 = compute_mean(R1, coeff)
m2 = compute_mean(R2, coeff)

print(m1)
# R1.root_nbhd(2).draw()
# plt.show()
print(m2)
# R2.root_nbhd(2).draw()
# plt.show()

T = 3000
m = 20
coeff = [0, 2, 0]
max_radius = 3

G_list = gen_data(T, m, coeff, seed = 19)

dist_R1_ER_list = []
dist_R2_ER_list = []
for G in G_list:
    R_list = make_R_list_nodes(G)
    closest_nbh_R1_ER, closest_nbh_dist_R1_ER = find_NN(R1, R_list, max_radius)
    closest_nbh_R2_ER, closest_nbh_dist_R2_ER = find_NN(R2, R_list, max_radius)
    dist_R1_ER_list.append(closest_nbh_dist_R1_ER)
    dist_R2_ER_list.append(closest_nbh_dist_R2_ER)


dist_R1_ER_list_new = []
dist_R2_ER_list_new = []

for i in range(len(G_list)):
    if dist_R1_ER_list[i] <= 1/(1+max_radius):
        dist_R1_ER_list_new.append(0)
    else:
        dist_R1_ER_list_new.append(dist_R1_ER_list[i])

    if dist_R2_ER_list[i] <= 1/(1+max_radius):
        dist_R2_ER_list_new.append(0)
    else:
        dist_R2_ER_list_new.append(dist_R2_ER_list[i])

datasets = [dist_R1_ER_list_new, dist_R2_ER_list_new]
network_names = [r'$g_1$', r'$g_2$']
# fig_file_name = 'EDF_distance_g12_ER.eps'
fig_file_name = 'Figure6-(a).eps'
plot_ecdfs_fig6(datasets, network_names, fig_file_name)



coeff = [0, 2, 0]

G_new = gen_data_WS_2_02(20, 20, coeff, seed = 6)[0]
R3 = root_network(G_new.subgraph(16), G_new)
R8 = root_network(G_new.subgraph(6), G_new)

m3 = compute_mean(R3, coeff)
m8 = compute_mean(R8, coeff)

print(m3)
# R3.root_nbhd(2).draw()
# plt.show()
print(m8)
# R8.root_nbhd(2).draw()
# plt.show()

T = 3000
m = 20
coeff = [0, 2, 0]
max_radius = 3

G_list = gen_data_WS_2_02(T, m, coeff, seed = 19)

dist_R3_WS_2_02_list = []
dist_R8_WS_2_02_list = []
for G in G_list:
    R_list = make_R_list_nodes(G)
    closest_nbh_R3_WS_2_02, closest_nbh_dist_R3_WS_2_02 = find_NN(R3, R_list, max_radius)
    closest_nbh_R8_WS_2_02, closest_nbh_dist_R8_WS_2_02 = find_NN(R8, R_list, max_radius)
    dist_R3_WS_2_02_list.append(closest_nbh_dist_R3_WS_2_02)
    dist_R8_WS_2_02_list.append(closest_nbh_dist_R8_WS_2_02)


dist_R3_WS_2_02_list_new = []
dist_R8_WS_2_02_list_new = []

for i in range(len(G_list)):
    if dist_R3_WS_2_02_list[i] <= 1/(1+max_radius):
        dist_R3_WS_2_02_list_new.append(0)
    else:
        dist_R3_WS_2_02_list_new.append(dist_R3_WS_2_02_list[i])

    if dist_R8_WS_2_02_list[i] <= 1/(1+max_radius):
        dist_R8_WS_2_02_list_new.append(0)
    else:
        dist_R8_WS_2_02_list_new.append(dist_R8_WS_2_02_list[i])

datasets = [dist_R3_WS_2_02_list_new, dist_R8_WS_2_02_list_new]
network_names = [r'$g_3$', r'$g_8$']
# fig_file_name = 'EDF_distance_g38_WS_2_02.eps'
fig_file_name = 'Figure6-(b).eps'
plot_ecdfs_fig6(datasets, network_names, fig_file_name)

coeff = [0, 2, 0]

G_new = gen_data_WS_2_08(20, 20, coeff, seed = 4)[0]
R6 = root_network(G_new.subgraph(5), G_new)
R7 = root_network(G_new.subgraph(15), G_new)

m6 = compute_mean(R6, coeff)
m7 = compute_mean(R7, coeff)

print(m6)
# R6.root_nbhd(2).draw()
# plt.show()
print(m7)
# R7.root_nbhd(2).draw()
# plt.show()

T = 3000
m = 20
coeff = [0, 2, 0]
max_radius = 3

G_list = gen_data_WS_2_08(T, m, coeff, seed = 19)

dist_R6_WS_2_08_list = []
dist_R7_WS_2_08_list = []
for G in G_list:
    R_list = make_R_list_nodes(G)
    closest_nbh_R6_WS_2_08, closest_nbh_dist_R6_WS_2_08 = find_NN(R6, R_list, max_radius)
    closest_nbh_R7_WS_2_08, closest_nbh_dist_R7_WS_2_08 = find_NN(R7, R_list, max_radius)
    dist_R6_WS_2_08_list.append(closest_nbh_dist_R6_WS_2_08)
    dist_R7_WS_2_08_list.append(closest_nbh_dist_R7_WS_2_08)


dist_R6_WS_2_08_list_new = []
dist_R7_WS_2_08_list_new = []

for i in range(len(G_list)):
    if dist_R6_WS_2_08_list[i] <= 1/(1+max_radius):
        dist_R6_WS_2_08_list_new.append(0)
    else:
        dist_R6_WS_2_08_list_new.append(dist_R6_WS_2_08_list[i])

    if dist_R7_WS_2_08_list[i] <= 1/(1+max_radius):
        dist_R7_WS_2_08_list_new.append(0)
    else:
        dist_R7_WS_2_08_list_new.append(dist_R7_WS_2_08_list[i])

datasets = [dist_R6_WS_2_08_list_new, dist_R7_WS_2_08_list_new]
network_names = [r'$g_6$', r'$g_7$']
# fig_file_name = 'EDF_distance_g67_WS_2_08.eps'
fig_file_name = 'Figure6-(c).eps'
plot_ecdfs_fig6(datasets, network_names, fig_file_name)



coeff = [0, 2, 0]

G_new = gen_data(1, 100, coeff, seed = 0)[0]

G_new2 = G_new.copy()
G_new3 = G_new.copy()
G_new2.add_edge(71, 4)
G_new2.add_node(200)
G_new2.add_edge(17,200)
G_new3.add_edge(4, 20)
G_new3.add_node(200)
G_new3.add_edge(17,200)
R1 = root_network(G_new2.subgraph(71), G_new2)
R2 = root_network(G_new3.subgraph(71), G_new3)

m1 = compute_mean(R1, coeff)
m2 = compute_mean(R2, coeff)

print(m1)
# R1.root_nbhd(2).draw()
# plt.show()
print(m2)
# R2.root_nbhd(2).draw()
# plt.show()

T = 3000
m = 20
coeff = [0, 2, 0]
max_radius = 3

G_list = gen_data_WS_2_0275(T, m, coeff, seed = 19)

dist_R1_WS_2_0275_list = []
dist_R2_WS_2_0275_list = []
for G in G_list:
    R_list = make_R_list_nodes(G)
    closest_nbh_R1_WS_2_0275, closest_nbh_dist_R1_WS_2_0275 = find_NN(R1, R_list, max_radius)
    closest_nbh_R2_WS_2_0275, closest_nbh_dist_R2_WS_2_0275 = find_NN(R2, R_list, max_radius)
    dist_R1_WS_2_0275_list.append(closest_nbh_dist_R1_WS_2_0275)
    dist_R2_WS_2_0275_list.append(closest_nbh_dist_R2_WS_2_0275)


dist_R1_WS_2_0275_list_new = []
dist_R2_WS_2_0275_list_new = []

for i in range(len(G_list)):
    if dist_R1_WS_2_0275_list[i] <= 1/(1+max_radius):
        dist_R1_WS_2_0275_list_new.append(0)
    else:
        dist_R1_WS_2_0275_list_new.append(dist_R1_WS_2_0275_list[i])

    if dist_R2_WS_2_0275_list[i] <= 1/(1+max_radius):
        dist_R2_WS_2_0275_list_new.append(0)
    else:
        dist_R2_WS_2_0275_list_new.append(dist_R2_WS_2_0275_list[i])

datasets = [dist_R2_WS_2_0275_list_new, dist_R2_WS_2_0275_list_new]
network_names = [r'$g_1$', r'$g_2$']
# fig_file_name = 'EDF_distance_g12_WS_2_0275.eps'
fig_file_name = 'Figure6-(d).eps'
plot_ecdfs_fig6(datasets, network_names, fig_file_name)




coeff = [0, 2, 0]

G_new = gen_data(1, 100, coeff, seed = 0)[0]
R4 = root_network(G_new.subgraph(41), G_new)
G_new4 = G_new.copy()
G_new4.add_edge(20, 71)
R5 = root_network(G_new4.subgraph(4), G_new4)

m4 = compute_mean(R4, coeff)
m5 = compute_mean(R5, coeff)

print(m4)
# R4.root_nbhd(2).draw()
# plt.show()
print(m5)
# R5.root_nbhd(2).draw()
# plt.show()

T = 3000
m = 20
coeff = [0, 2, 0]
max_radius = 3

G_list = gen_data_RG(T, m, coeff, seed = 19)

dist_R4_RG_list = []
dist_R5_RG_list = []
for G in G_list:
    R_list = make_R_list_nodes(G)
    closest_nbh_R4_RG, closest_nbh_dist_R4_RG = find_NN(R4, R_list, max_radius)
    closest_nbh_R5_RG, closest_nbh_dist_R5_RG = find_NN(R5, R_list, max_radius)
    dist_R4_RG_list.append(closest_nbh_dist_R4_RG)
    dist_R5_RG_list.append(closest_nbh_dist_R5_RG)


dist_R4_RG_list_new = []
dist_R5_RG_list_new = []

for i in range(len(G_list)):
    if dist_R4_RG_list[i] <= 1/(1+max_radius):
        dist_R4_RG_list_new.append(0)
    else:
        dist_R4_RG_list_new.append(dist_R4_RG_list[i])

    if dist_R5_RG_list[i] <= 1/(1+max_radius):
        dist_R5_RG_list_new.append(0)
    else:
        dist_R5_RG_list_new.append(dist_R5_RG_list[i])

datasets = [dist_R4_RG_list_new, dist_R5_RG_list_new]
network_names = [r'$g_4$', r'$g_5$']
# fig_file_name = 'EDF_distance_g45_RG.eps'
fig_file_name = 'Figure6-(e).eps'
plot_ecdfs_fig6(datasets, network_names, fig_file_name)



G_new = gen_data(1, 100, coeff, seed = 0)[0]

G_new2 = G_new.copy()
G_new3 = G_new.copy()
G_new2.add_edge(71, 4)
G_new2.add_node(200)
G_new2.add_edge(17,200)
G_new3.add_edge(4, 20)
G_new3.add_node(200)
G_new3.add_edge(17,200)
R1 = root_network(G_new2.subgraph(71), G_new2)
R2 = root_network(G_new3.subgraph(71), G_new3)

m1 = compute_mean(R1, coeff)
m2 = compute_mean(R2, coeff)

print(m1)
# R1.root_nbhd(2).draw()
# plt.show()
print(m2)
# R2.root_nbhd(2).draw()
# plt.show()

T = 3000
m = 20
coeff = [0, 2, 0]
max_radius = 3

G_list = gen_data_RG(T, m, coeff, seed = 19)

dist_R1_RG_list = []
dist_R2_RG_list = []
for G in G_list:
    R_list = make_R_list_nodes(G)
    closest_nbh_R1_RG, closest_nbh_dist_R1_RG = find_NN(R1, R_list, max_radius)
    closest_nbh_R2_RG, closest_nbh_dist_R2_RG = find_NN(R2, R_list, max_radius)
    dist_R1_RG_list.append(closest_nbh_dist_R1_RG)
    dist_R2_RG_list.append(closest_nbh_dist_R2_RG)


dist_R1_RG_list_new = []
dist_R2_RG_list_new = []

for i in range(len(G_list)):
    if dist_R1_RG_list[i] <= 1/(1+max_radius):
        dist_R1_RG_list_new.append(0)
    else:
        dist_R1_RG_list_new.append(dist_R1_RG_list[i])

    if dist_R2_RG_list[i] <= 1/(1+max_radius):
        dist_R2_RG_list_new.append(0)
    else:
        dist_R2_RG_list_new.append(dist_R2_RG_list[i])

datasets = [dist_R1_RG_list_new, dist_R2_RG_list_new]
network_names = [r'$g_1$', r'$g_2$']
# fig_file_name = 'EDF_distance_g12_RG.eps'
fig_file_name = 'Figure6-(f).eps'
plot_ecdfs_fig6(datasets, network_names, fig_file_name)



coeff = [0, 2, 0]

G_new = gen_data_WS_2_02(20, 20, coeff, seed = 6)[0]
R3 = root_network(G_new.subgraph(16), G_new)

G_new = gen_data(1, 100, coeff, seed = 0)[0]
R4 = root_network(G_new.subgraph(41), G_new)
R9 = root_network(G_new.subgraph(87), G_new)
R0 = root_network(G_new.subgraph(36), G_new)

m3 = compute_mean(R3, coeff)
m4 = compute_mean(R4, coeff)
m9 = compute_mean(R9, coeff)
m0 = compute_mean(R0, coeff)

print(m3)
# R3.root_nbhd(2).draw()
# plt.show()
print(m4)
# R4.root_nbhd(2).draw()
# plt.show()
print(m9)
# R9.root_nbhd(2).draw()
# plt.show()
print(m0)
# R0.root_nbhd(2).draw()
# plt.show()

T = 3000
m = 20
coeff = [0, 2, 0]
max_radius = 3

G_list = gen_data(T, m, coeff, seed = 19)

dist_R3_ER_list = []
dist_R4_ER_list = []
dist_R9_ER_list = []
dist_R0_ER_list = []
for G in G_list:
    R_list = make_R_list_nodes(G)
    closest_nbh_R3_ER, closest_nbh_dist_R3_ER = find_NN(R3, R_list, max_radius)
    closest_nbh_R4_ER, closest_nbh_dist_R4_ER = find_NN(R4, R_list, max_radius)
    closest_nbh_R9_ER, closest_nbh_dist_R9_ER = find_NN(R9, R_list, max_radius)
    closest_nbh_R0_ER, closest_nbh_dist_R0_ER = find_NN(R0, R_list, max_radius)
    dist_R3_ER_list.append(closest_nbh_dist_R3_ER)
    dist_R4_ER_list.append(closest_nbh_dist_R4_ER)
    dist_R9_ER_list.append(closest_nbh_dist_R9_ER)
    dist_R0_ER_list.append(closest_nbh_dist_R0_ER)


dist_R3_ER_list_new = []
dist_R4_ER_list_new = []
dist_R9_ER_list_new = []
dist_R0_ER_list_new = []

for i in range(len(G_list)):
    if dist_R3_ER_list[i] <= 1/(1+max_radius):
        dist_R3_ER_list_new.append(0)
    else:
        dist_R3_ER_list_new.append(dist_R3_ER_list[i])

    if dist_R4_ER_list[i] <= 1/(1+max_radius):
        dist_R4_ER_list_new.append(0)
    else:
        dist_R4_ER_list_new.append(dist_R4_ER_list[i])

    if dist_R9_ER_list[i] <= 1/(1+max_radius):
        dist_R9_ER_list_new.append(0)
    else:
        dist_R9_ER_list_new.append(dist_R9_ER_list[i])

    if dist_R0_ER_list[i] <= 1/(1+max_radius):
        dist_R0_ER_list_new.append(0)
    else:
        dist_R0_ER_list_new.append(dist_R0_ER_list[i])



def plot_ecdfs_fig7(datasets, network_names, fig_file_name):
    # Create a figure with subplots for each dataset
    fig, axes = plt.subplots(1, len(datasets), figsize=(20, 5), sharey=True)
    
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

datasets = [dist_R3_ER_list_new, dist_R4_ER_list_new, dist_R9_ER_list_new, dist_R0_ER_list_new]
network_names = [r'$g_3$', r'$g_4$', r'$g_9$', r'$g_0$']
# fig_file_name = 'EDF_distance_g3490_ER.eps'
fig_file_name = 'Figure7.eps'
plot_ecdfs_fig7(datasets, network_names, fig_file_name)

end = timer()

print("running time:", end - start)

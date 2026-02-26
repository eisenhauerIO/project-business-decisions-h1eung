import numpy as np
import networkx as nx
import networkx.algorithms.isomorphism as iso
import random
import copy
import pandas as pd
import matplotlib.pyplot as plt
from timeit import default_timer as timer
import os
import re
from decimal import Decimal

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


def run_sim(T, m, coeff, k_set, itera = 1000):
    # k_set = [1, 5, 10, 20, 50, 75, 100]
    start = timer()
    
    print("T:", T, " m:", m)
    print("coeff:", coeff)
    
    G_new = gen_data(1, 100, coeff, seed = 0)[0]

    R3 = root_network(G_new.subgraph(71), G_new)
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

    
    mse3 = np.zeros((itera, len(k_set)))
    mse4 = np.zeros((itera, len(k_set)))
    mse9 = np.zeros((itera, len(k_set)))
    mse0 = np.zeros((itera, len(k_set)))

    for i in range(itera):
        G_list = gen_data(T, m, coeff, seed = i + 1)
        e3, b3, c3 = ASF_hat_ave(R3, G_list, 2, k_set)
        mse3[i,:] = (e3 - m3)**2
        e4, b4, c4 = ASF_hat_ave(R4, G_list, 2, k_set)
        mse4[i,:] = (e4 - m4)**2
        e9, b9, c9 = ASF_hat_ave(R9, G_list, 2, k_set)
        mse9[i,:] = (e9 - m9)**2
        e0, b0, c0 = ASF_hat_ave(R0, G_list, 2, k_set)
        mse0[i,:] = (e0 - m0)**2
                
    mean_mse3 = np.mean(mse3, axis = 0)
    mean_mse4 = np.mean(mse4, axis = 0)
    mean_mse9 = np.mean(mse9, axis = 0)
    mean_mse0 = np.mean(mse0, axis = 0)

    print("C = ", T)
    print("coeff_1 = ", coeff[0])
    print("coeff_2 = ", coeff[1])
    print("mse3:", mean_mse3)
    print("mse4:", mean_mse4)
    print("mse9:", mean_mse9)
    print("mse0:", mean_mse0)

    end = timer()
    
    with open(f"simulation_mse_ave_C{T}_coeff{coeff[0]}_{coeff[1]}.txt", 'w') as my_output:
            my_output.write("mse3: " + ", ".join(["%f" % x for x in mean_mse3]) + "\n")
            my_output.write("mse4: " + ", ".join(["%f" % x for x in mean_mse4]) + "\n")
            my_output.write("mse9: " + ", ".join(["%f" % x for x in mean_mse9]) + "\n")
            my_output.write("mse0: " + ", ".join(["%f" % x for x in mean_mse0]) + "\n")
            my_output.write("Running time: %f \n" % (end - start))

T = 20
m = 20
coeff = [1,0,0]
k_set = [5, 10, 20]
itera = 1000

run_sim(T, m, coeff, k_set, itera)

T = 20
m = 20
coeff = [1,0.5,0]
k_set = [5, 10, 20]
itera = 1000

run_sim(T, m, coeff, k_set, itera)

T = 50
m = 20
coeff = [1,0,0]
k_set = [5, 10, 20, 50]
itera = 1000

run_sim(T, m, coeff, k_set, itera)

T = 50
m = 20
coeff = [1,0.5,0]
k_set = [5, 10, 20, 50]
itera = 1000

run_sim(T, m, coeff, k_set, itera)

T = 100
m = 20
coeff = [1,0,0]
k_set = [5, 10, 20, 50, 75, 100]
itera = 1000

run_sim(T, m, coeff, k_set, itera)

T = 100
m = 20
coeff = [1,0.5,0]
k_set = [5, 10, 20, 50, 75, 100]
itera = 1000

run_sim(T, m, coeff, k_set, itera)

## Latex output of Table 

# Function to extract the number after ":" in the first line that has it
def extract_number(file_path, graph_number):
    try:
        with open(file_path, 'r') as f:
            for line in f:
                if line.startswith(f"mse{graph_number}:"):
                    # Extract all float numbers from the line using regex
                    numbers = list(re.findall(r"[\d.]+", line))
                    return numbers[1:]
                else:
                    continue
    except FileNotFoundError:
        return ""

# Define T values and corresponding q ranges
def txt_to_row_list(coeff, graph_number, directory):
    
    Ts = [20, 50, 100]
    row_list = []
    for T in Ts:
        file_path = directory + r"/" + f"simulation_mse_ave_C{T}_coeff{coeff[0]}_{coeff[1]}.txt"
        row_list += extract_number(file_path, graph_number)

    return row_list


def list_to_table(L):
    # L is a list (a row in the table)
    table_row = ""
    for i in range(len(L)-1):
        if L[i] == "":
            table_row = table_row + " " + r"&"
        else:
            number_str = str(Decimal(L[i]).quantize(Decimal("0.01"), rounding = "ROUND_HALF_UP"))
            table_row = table_row + number_str + r"&"
    if L[-1] == "":
        table_row = table_row + " " + r"\\"
    else:
        number_str = str(Decimal(L[-1]).quantize(Decimal("0.01"), rounding = "ROUND_HALF_UP"))
        table_row = table_row + number_str + r"\\"
    return table_row
    
# Set directory where files are located
directory = os.getcwd()

with open(f"Table11.txt", 'w') as my_output:
    my_output.write(r"\begin{table}[htbp]")
    my_output.write(r"\scriptsize")
    my_output.write(r"\centering")
    my_output.write(r"\caption{Estimated MSEs \\ ($1,000$ Monte Carlo iterations)}")
    my_output.write(r"\begin{tabular}{rcccc|cccc|cccccc}")
    my_output.write(r"\toprule")
    my_output.write(r"& \multicolumn{1}{r}{} &       & $C = 20$ & \multicolumn{1}{r}{} &       & $C = 50$ &       & \multicolumn{1}{r}{} &       &       & $C = 100$ &       &       &  \\")
    my_output.write(r"& \multicolumn{1}{r}{} &       & $k$     & \multicolumn{1}{c}{} &       & $k$     &       & \multicolumn{1}{r}{} &       &       & $k$     &       &       &  \\")
    my_output.write(r"\cmidrule{3-15}    \multicolumn{1}{c}{$\theta$} & \multicolumn{1}{c}{$g_{\iota}$} & 5     & 10    & \multicolumn{1}{c}{20}    & 5     & 10    & 20    & \multicolumn{1}{c}{50}    & 5     & 10    & 20    & 50    & 75    & 100 \\")
    my_output.write(r"\midrule")

    graph_set = [3,4,9,0]
    for graph_number in graph_set:
        if graph_number == 4:
            my_output.write(r" \multicolumn{1}{c}{$(1, 0)$} &" + f"$g_{graph_number}$" + "&" + list_to_table(txt_to_row_list([1,0], graph_number, directory)))
        else:
            my_output.write(r"&" + f"$g_{graph_number}$" + "&" + list_to_table(txt_to_row_list([1,0], graph_number, directory)))

    my_output.write(r"\midrule")
    for graph_number in graph_set:
        if graph_number == 4:
            my_output.write(r" \multicolumn{1}{c}{$(1, 0.5)$} &" + f"$g_{graph_number}$" + "&" + list_to_table(txt_to_row_list([1,0.5], graph_number, directory)))
        else:
            my_output.write(r"&" + f"$g_{graph_number}$" + "&" + list_to_table(txt_to_row_list([1,0.5], graph_number, directory)))

    my_output.write(r"\bottomrule")
    my_output.write(r"\end{tabular}")
    my_output.write(r"\label{tab:MSE_results_averaging}")
    my_output.write(r"\end{table}")


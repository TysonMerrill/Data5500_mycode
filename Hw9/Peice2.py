'''
import requests
import json
import time
import os
from datetime import datetime, timedelta
from itertools import permutations
from itertools import combinations

import networkx as nx
from networkx.classes.function import path_weight

import matplotlib.pyplot as plt


currencies = ["usd", "eur", "gbp", "mxn", "rub", "inr"]

g = nx.DiGraph()
edges = []

############################################################
# Querying floatrates.com for currency exchange rates
url1 = "http://www.floatrates.com/daily/"
url2 = ".json"
for c1, c2 in permutations(currencies,2): # querying all permutations of currency pairs
    url = url1 + c1 + url2
    print(c1, "to", c2, url)
    
    req = requests.get(url)
    dct1 = json.loads(req.text)
    rate = dct1[c2]["rate"]
    edges.append((c1, c2, rate))
print(edges)    
g.add_weighted_edges_from(edges) 



############################################################
# Saving Graph Visual
curr_dir = os.path.dirname(__file__) # get the current directory of this file
graph_visual_fil = curr_dir + "/" + "currencies_graph_visual.png"

pos=nx.circular_layout(g) # pos = nx.nx_agraph.graphviz_layout(G)
nx.draw_networkx(g,pos)
labels = nx.get_edge_attributes(g,'weight')
nx.draw_networkx_edge_labels(g,pos,edge_labels=labels)

plt.savefig(graph_visual_fil)

###########################################################
# STEP 2 - Traverse Graph 
# for each node pair, find paths between them
# calculate the path weight, 
for n1, n2 in permutations(g.nodes,2): #permutations returns all pairs
    print("all existing paths from", n1, "to", n2, ":")
    
    # all_simple_paths function below returns each path as a list
    # the graph can be accessed with the nodes as keys, like a dictionary
    # g['v0']['v1']['weight'] returns 2, the weight of that edge
    # iterating through the edges in a path, you can calculate the weight of the entire path
    
    for path in nx.all_simple_paths(g, source=n1, target=n2):
        print(path) # print each path
        path_weight = 0
        
        # iterating through each edge in the path and adding edge weight to total path weight
        for i in range(len(path) - 1):
            path_weight += g[path[i]][path[i+1]]['weight']
        print("path_weight: ", path_weight)
        
'''
def calculate_path_weight(g, path):
    """
    Calculate the weight of a path by multiplying all edge weights
    """
    path_weight = 1.0
    for i in range(len(path) - 1):
        path_weight *= g[path[i]][path[i+1]]['weight']
    return path_weight

def find_arbitrage_opportunities(g):
    """
    Find potential arbitrage opportunities between all pairs of currencies, excluding ada
    """
    min_path_weight_factor = float('inf')
    max_path_weight_factor = 0.0
    min_paths = None
    max_paths = None
    
    # Get all currency nodes except ada
    nodes = [node for node in g.nodes() if node != 'ada']
    
    # Process all combinations of currency pairs
    for node1 in nodes:
        for node2 in nodes:
            if node1 == node2:  # Skip same node
                continue
            
            print(f"\npaths from {node1} to {node2} ----------------------------------")
            
            # Find all paths from node1 to node2
            try:
                # Get paths with reasonable length limit
                all_paths_1_to_2 = []
                
                # Find paths that don't include ada
                for path in nx.all_simple_paths(g, node1, node2, cutoff=6):
                    if 'ada' not in path:
                        all_paths_1_to_2.append(path)
                
                if not all_paths_1_to_2:
                    print(f"No valid paths found from {node1} to {node2}")
                    continue
                
                for path_1_to_2 in all_paths_1_to_2:
                    # Calculate weight of path from node1 to node2
                    weight_1_to_2 = calculate_path_weight(g, path_1_to_2)
                    print(f"{path_1_to_2} {weight_1_to_2}")
                    
                    # Find all paths from node2 to node1 that don't include ada
                    all_paths_2_to_1 = []
                    
                    try:
                        for path in nx.all_simple_paths(g, node2, node1, cutoff=6):
                            if 'ada' not in path:
                                all_paths_2_to_1.append(path)
                        
                        if not all_paths_2_to_1:
                            print(f"No valid paths found from {node2} back to {node1}")
                            continue
                        
                        for path_2_to_1 in all_paths_2_to_1:
                            # Calculate weight of path from node2 to node1
                            weight_2_to_1 = calculate_path_weight(g, path_2_to_1)
                            print(f"{path_2_to_1} {weight_2_to_1}")
                            
                            # Calculate path weights factor (should be ~1.0 if equilibrium)
                            path_weight_factor = weight_1_to_2 * weight_2_to_1
                            print(f"{path_weight_factor}")
                            
                            # Check if this is smallest or greatest factor
                            factor_distance = abs(path_weight_factor - 1.0)
                            
                            if factor_distance < min_path_weight_factor:
                                min_path_weight_factor = factor_distance
                                min_paths = (path_1_to_2, path_2_to_1)
                            
                            if path_weight_factor > 1.0 and path_weight_factor > max_path_weight_factor:
                                max_path_weight_factor = path_weight_factor
                                max_paths = (path_1_to_2, path_2_to_1)
                    
                    except nx.NetworkXNoPath:
                        print(f"No path found from {node2} back to {node1}")
            
            except nx.NetworkXNoPath:
                print(f"No path found from {node1} to {node2}")
    
    # Display results
    print("\n\nFinal Results:")
    if min_paths:
        print(f"Smallest Paths weight factor: {min_path_weight_factor + 1.0:.8f}")
        print(f"Paths: {min_paths[0]} {min_paths[1]}")
    else:
        print("No minimum path factor found.")
        
    if max_paths:
        print(f"Greatest Paths weight factor: {max_path_weight_factor:.8f}")
        print(f"Paths: {max_paths[0]} {max_paths[1]}")
    else:
        print("No maximum path factor found.")
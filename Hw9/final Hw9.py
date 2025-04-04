import requests
import networkx as nx
import matplotlib.pyplot as plt
import os
from datetime import datetime

def get_crypto_rates():
    """
    Fetch cryptocurrency exchange rates from CoinGecko API and return them as edges
    """
    url = "https://api.coingecko.com/api/v3/simple/price?ids=ethereum,bitcoin,litecoin,ripple,cardano,bitcoin-cash,eos&vs_currencies=eth,btc,ltc,xrp,ada,bch,eos"
    req = requests.get(url)
    
    edges = []
    
    if req.status_code == 200:
        data = req.json()
        
        # Mapping full names to abbreviations
        abbreviations = {
            "ethereum": "eth",
            "bitcoin": "btc",
            "litecoin": "ltc",
            "ripple": "xrp",
            "cardano": "ada",
            "bitcoin-cash": "bch",
            "eos": "eos"
        }
        
        # Add crypto rates to edges list
        for base_currency, rates in data.items():
            base_abbr = abbreviations.get(base_currency, base_currency)
            for target_currency, rate in rates.items():
                target_abbr = target_currency  # API already returns abbreviations for vs_currencies
                if base_abbr != target_abbr:  # Exclude conversions to itself
                    edges.append((base_abbr, target_abbr, rate))
        
        # Save the exchange rates to a text file with timestamp
        timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        file_path = f"exchange_rates_{timestamp}.txt"
        
        with open(file_path, "w") as txt_file:
            for edge in edges:
                txt_file.write(f"{edge[0]},{edge[1]},{edge[2]}\n")
                
        print(f"Exchange rates saved to {file_path}")
        return edges
    else:
        print(f"Failed to fetch exchange rates. Status code: {req.status_code}")
        return []

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

def main():
    # Initialize Graph
    g = nx.DiGraph()
    
    # Get cryptocurrency exchange rates
    edges = get_crypto_rates()
    
    # Add edges to the graph
    g.add_weighted_edges_from(edges)
    
    # Save graph visualization
    try:
        curr_dir = os.path.dirname(os.path.abspath(__file__))
    except:
        curr_dir = os.getcwd()
    
    graph_visual_file = os.path.join(curr_dir, "crypto_graph_visual.png")
    
    # Visualize the graph
    pos = nx.circular_layout(g)
    plt.figure(figsize=(12, 8))
    nx.draw_networkx(g, pos)
    labels = nx.get_edge_attributes(g, 'weight')
    nx.draw_networkx_edge_labels(g, pos, edge_labels=labels)
    plt.savefig(graph_visual_file)
    plt.close()
    print(f"Graph saved as {graph_visual_file}")
    
    # Find arbitrage opportunities
    find_arbitrage_opportunities(g)

if __name__ == "__main__":
    main()
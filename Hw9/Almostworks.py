import requests
import json
import networkx as nx
import matplotlib.pyplot as plt
import os
from datetime import datetime
from itertools import permutations

def get_crypto_rates():
    """
    Fetch cryptocurrency exchange rates from CoinGecko API and return them as edges
    """
    # Define cryptocurrencies to use
    cryptocurrencies = ["ethereum", "bitcoin", "litecoin", "ripple", "cardano", "bitcoin-cash", "eos"]
    abbreviations = {
        "ethereum": "eth",
        "bitcoin": "btc",
        "litecoin": "ltc",
        "ripple": "xrp",
        "cardano": "ada",
        "bitcoin-cash": "bch",
        "eos": "eos"
    }
    
    edges = []
    
    # Build URL for all currencies
    currencies_param = ",".join(cryptocurrencies)
    vs_currencies_param = ",".join([abbreviations[crypto] for crypto in cryptocurrencies])
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={currencies_param}&vs_currencies={vs_currencies_param}"
    
    print(f"Fetching crypto rates from: {url}")
    req = requests.get(url)
    
    if req.status_code == 200:
        data = json.loads(req.text)
        
        # Add crypto rates to edges list
        for base_currency, rates in data.items():
            base_abbr = abbreviations.get(base_currency, base_currency)
            for target_currency, rate in rates.items():
                if base_abbr != target_currency:  # Exclude conversions to itself
                    print(f"{base_abbr} to {target_currency}: {rate}")
                    edges.append((base_abbr, target_currency, rate))
        
        # Save the exchange rates to a text file with timestamp
        timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        file_path = f"exchange_rates_{timestamp}.txt"
        
        with open(file_path, "w") as txt_file:
            for edge in edges:
                txt_file.write(f"{edge[0]},{edge[1]},{edge[2]}\n")
                
        print(f"Exchange rates saved to {file_path}")
    else:
        print(f"Failed to fetch exchange rates. Status code: {req.status_code}")
    
    print(edges)
    return edges

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
    Find potential arbitrage opportunities between all pairs of currencies
    """
    # Track min and max arbitrage opportunities
    min_arbitrage = {"factor": float('inf'), "paths": None, "n1": None, "n2": None}
    max_arbitrage = {"factor": 0.0, "paths": None, "n1": None, "n2": None}
    
    # Get all currency nodes except ada (as per original code)
    nodes = [node for node in g.nodes() if node != 'ada']
    
    # Process all combinations of currency pairs
    for n1, n2 in permutations(nodes, 2):
        print("\nAll existing paths from", n1, "to", n2, ":")
        
        # Find paths with reasonable length limit that don't include ada
        all_paths_1_to_2 = []
        try:
            for path in nx.all_simple_paths(g, n1, n2, cutoff=6):
                if 'ada' not in path:
                    all_paths_1_to_2.append(path)
                    print(path)
                    weight_1_to_2 = calculate_path_weight(g, path)
                    print("path_weight:", weight_1_to_2)
            
            if not all_paths_1_to_2:
                print(f"No valid paths found from {n1} to {n2}")
                continue
                
            # Now find paths back from n2 to n1
            print("\nAll existing paths from", n2, "to", n1, ":")
            all_paths_2_to_1 = []
            
            for path in nx.all_simple_paths(g, n2, n1, cutoff=6):
                if 'ada' not in path:
                    all_paths_2_to_1.append(path)
                    print(path)
                    weight_2_to_1 = calculate_path_weight(g, path)
                    print("path_weight:", weight_2_to_1)
            
            if not all_paths_2_to_1:
                print(f"No valid paths found from {n2} back to {n1}")
                continue
            
            # Calculate arbitrage opportunities
            print("\nArbitrage opportunities between", n1, "and", n2, ":")
            for path_1_to_2 in all_paths_1_to_2:
                weight_1_to_2 = calculate_path_weight(g, path_1_to_2)
                
                for path_2_to_1 in all_paths_2_to_1:
                    weight_2_to_1 = calculate_path_weight(g, path_2_to_1)
                    
                    # Calculate path weights factor (should be ~1.0 if equilibrium)
                    path_weight_factor = weight_1_to_2 * weight_2_to_1
                    print(f"Round trip factor: {path_weight_factor:.8f}")
                    print(f"Forward: {path_1_to_2} ({weight_1_to_2:.8f})")
                    print(f"Return: {path_2_to_1} ({weight_2_to_1:.8f})")
                    
                    # Check for smallest difference from 1.0 (closest to equilibrium)
                    factor_distance = abs(path_weight_factor - 1.0)
                    if factor_distance < min_arbitrage["factor"]:
                        min_arbitrage["factor"] = factor_distance
                        min_arbitrage["paths"] = (path_1_to_2, path_2_to_1)
                        min_arbitrage["weights"] = (weight_1_to_2, weight_2_to_1)
                        min_arbitrage["n1"] = n1
                        min_arbitrage["n2"] = n2
                    
                    # Check for largest factor (best arbitrage opportunity)
                    if path_weight_factor > max_arbitrage["factor"]:
                        max_arbitrage["factor"] = path_weight_factor
                        max_arbitrage["paths"] = (path_1_to_2, path_2_to_1)
                        max_arbitrage["weights"] = (weight_1_to_2, weight_2_to_1)
                        max_arbitrage["n1"] = n1
                        max_arbitrage["n2"] = n2
                    
        except nx.NetworkXNoPath:
            print(f"No path found between {n1} and {n2}")
    
    # Display results
    print("\n" + "="*80)
    print("ARBITRAGE SUMMARY:")
    print("="*80)
    
    print("\nSMALLEST ARBITRAGE (closest to equilibrium):")
    print(f"Factor distance from 1.0: {min_arbitrage['factor']:.8f}")
    print(f"Actual factor: {1.0 + min_arbitrage['factor']:.8f}")
    print(f"From {min_arbitrage['n1']} to {min_arbitrage['n2']} and back:")
    print(f"Forward path: {min_arbitrage['paths'][0]} (weight: {min_arbitrage['weights'][0]:.8f})")
    print(f"Return path: {min_arbitrage['paths'][1]} (weight: {min_arbitrage['weights'][1]:.8f})")
    
    print("\nBIGGEST ARBITRAGE OPPORTUNITY:")
    print(f"Factor: {max_arbitrage['factor']:.8f}")
    print(f"From {max_arbitrage['n1']} to {max_arbitrage['n2']} and back:")
    print(f"Forward path: {max_arbitrage['paths'][0]} (weight: {max_arbitrage['weights'][0]:.8f})")
    print(f"Return path: {max_arbitrage['paths'][1]} (weight: {max_arbitrage['weights'][1]:.8f})")
    print("="*80)

def main():
    # Initialize Graph
    g = nx.DiGraph()
    
    # Get cryptocurrency exchange rates
    edges = get_crypto_rates()
    
    # Add edges to the graph
    g.add_weighted_edges_from(edges)
    
    ############################################################
    # Saving Graph Visual
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
    
    ############################################################
    # Find arbitrage opportunities
    find_arbitrage_opportunities(g)

if __name__ == "__main__":
    main()
import requests
import json
from datetime import datetime

# Function to fetch and save cryptocurrency exchange rates
def get_crypto_rates():
    url = "https://api.coingecko.com/api/v3/simple/price?ids=ethereum,bitcoin,litecoin,ripple,cardano,bitcoin-cash,eos&vs_currencies=eth,btc,ltc,xrp,ada,bch,eos"
    req = requests.get(url)
    
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
        
        # Reverse the mapping to handle API response keys
        reverse_abbreviations = {v: k for k, v in abbreviations.items()}
        
        # Save the exchange rates to a text file with timestamp
        timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        file_path = f"/home/ubuntu/Data5500_mycode/Hw9/exchange_rates_{timestamp}.txt"
        
        with open(file_path, "w") as txt_file:
            for base_currency, rates in data.items():
                base_abbr = abbreviations.get(base_currency, base_currency)  # Convert to abbreviation
                for target_currency, rate in rates.items():
                    target_abbr = abbreviations.get(target_currency, target_currency)  # Ensure target currency abbreviation
                    if base_abbr != target_abbr:  # Exclude conversions to itself
                        txt_file.write(f"{base_abbr},{target_abbr},{rate}\n")
        
        print(f"Exchange rates saved to {file_path}")
    else:
        print("Failed to fetch exchange rates.")

# Run the function
get_crypto_rates()

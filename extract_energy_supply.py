import os

import re

def extract_energy_supply():
    base_dir = '/home/edwinnoe/SIMULACION_PROYECTO/oferta_energia'
    years = range(2005, 2021)
    results = {}

    for year in years:
        # Determine filename
        if year == 2020:
            filename = 'oferta_2020.csv'
        else:
            filename = f'Oferta de energia {year}.csv'
        
        filepath = os.path.join(base_dir, filename)
        
        if not os.path.exists(filepath):
            print(f"File not found: {filepath}")
            continue
            
        try:
            # Read CSV. It seems to have a header on line 10 (0-indexed) or so.
            # Let's read the whole file as text first to find the "Oferta total" line.
            with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
                lines = f.readlines()
            
            oferta_total_line = None
            for line in lines:
                if "Oferta total" in line:
                    oferta_total_line = line
                    break
            
            if oferta_total_line:
                parts = oferta_total_line.split(',')
                # The last element should be the Total Primary Energy
                # Be careful with empty strings or newlines
                val_str = parts[-1].strip()
                if not val_str: # Try the one before if empty (trailing comma)
                    val_str = parts[-2].strip()
                
                # Remove quotes if any
                val_str = val_str.replace('"', '')
                
                try:
                    val = float(val_str)
                    results[year] = val
                except ValueError:
                    print(f"Could not parse value '{val_str}' for year {year}")
            else:
                print(f"Could not find 'Oferta total' in {filename}")

        except Exception as e:
            print(f"Error processing {year}: {e}")

    print("--- EXTRACTED VALUES (Oferta Total) ---")
    for year in years:
        if year in results:
            print(f"{year}: {results[year]}")
        else:
            print(f"{year}: NOT FOUND")

if __name__ == "__main__":
    extract_energy_supply()

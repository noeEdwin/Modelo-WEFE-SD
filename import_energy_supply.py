import csv
import psycopg2
from config import DB_CONFIG

def parse_csv(filepath):
    """Parse the specific format of the energy supply CSV"""
    data = {}
    current_year = None
    
    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        for row in reader:
            if not row:
                continue
                
            # Check for year (assuming it's in the first column and is a 4-digit number)
            if row[0].isdigit() and len(row[0]) == 4:
                current_year = int(row[0])
                continue
            
            # Check for "Oferta total" row
            if row[0] == "Oferta total" and current_year:
                # The last column seems to be the total, but let's be safe and take the last non-empty one
                # or specifically the 13th column (index 12) based on the header
                # Header: ,Carbón,Petróleo crudo,Condensados,Gas natural,Nucleo-energía,Hidro-energía,Geoenergía,Energía solar,Energía eólica,Bagazo de caña,Leña,Biogás,Total de energía primaria
                # Indices: 0      1              2               3           4           5              6             7          8             9             10             11    12      13
                # Wait, the header has an empty first column.
                # Let's look at the row: "Oferta total", val, val...
                # The last value is the total.
                try:
                    total_val = float(row[-1].replace(',', ''))
                    data[current_year] = total_val
                    print(f"Found data for {current_year}: {total_val}")
                except ValueError:
                    print(f"Could not parse value for {current_year}: {row[-1]}")
                
                current_year = None # Reset after finding the value for the year

    return data

def update_database(data):
    """Update the database with the parsed data"""
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    
    for year, value in data.items():
        print(f"Updating {year} with {value}...")
        query = """
            UPDATE validacion_historica_mexico
            SET oferta_energia_real = %s
            WHERE anio = %s;
        """
        cur.execute(query, (value, year))
        
        if cur.rowcount == 0:
            print(f"Warning: No record found for year {year}")
            
    conn.commit()
    cur.close()
    conn.close()
    print("Database update complete.")

if __name__ == "__main__":
    csv_path = "oferta_energia.csv"
    print(f"Reading {csv_path}...")
    energy_data = parse_csv(csv_path)
    
    if energy_data:
        print(f"Found {len(energy_data)} records. Updating database...")
        update_database(energy_data)
    else:
        print("No data found in CSV.")

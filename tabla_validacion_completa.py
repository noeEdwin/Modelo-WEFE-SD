import psycopg2
import pandas as pd
import json
from config import DB_CONFIG
from wefe_model import WEFEModel

def get_real_data():
    """Fetch historical data from Postgres"""
    conn = psycopg2.connect(**DB_CONFIG)
    query = "SELECT * FROM validacion_historica_mexico ORDER BY anio ASC"
    df = pd.read_sql(query, conn)
    conn.close()
    return df

def run_simulation():
    """Run model with base config"""
    with open('config_mexico_2005.json', 'r') as f:
        config = json.load(f)
    
    model = WEFEModel(
        initial_data=config['initial_data'],
        params=config['params'],
        scenarios=config['scenarios']
    )
    return model.run(years=16)

def print_variable_table(var_name, real_values, sim_values, years):
    """Print formatted table for a single variable"""
    print(f"\n{'='*80}")
    print(f"VARIABLE: {var_name}")
    print(f"{'='*80}")
    print(f"{'Año':<6} | {'Dato Real':>15} | {'Dato Simulado':>15} | {'Diferencia':>15} | {'Error (%)':>10}")
    print(f"{'-'*80}")
    
    errors = []
    for i, year in enumerate(years):
        real = real_values[i]
        sim = sim_values[i]
        diff = sim - real
        error_pct = abs(diff / real) * 100 if real != 0 else 0
        errors.append(error_pct)
        
        print(f"{year:<6} | {real:>15,.2f} | {sim:>15,.2f} | {diff:>15,.2f} | {error_pct:>9.2f}%")
    
    avg_error = sum(errors) / len(errors)
    print(f"{'-'*80}")
    print(f"ERROR PROMEDIO (MAPE): {avg_error:.2f}%")
    print(f"{'='*80}")

def main():
    print("🔍 Obteniendo datos reales y ejecutando simulación...\n")
    real_df = get_real_data()
    sim_df = run_simulation()
    
    years = real_df['anio'].values
    
    # 1. POBLACIÓN
    print_variable_table(
        "POBLACIÓN",
        real_df['poblacion_real'].values,
        sim_df['population'].values,
        years
    )
    
    # 2. PIB
    print_variable_table(
        "PIB (Pesos MXN)",
        real_df['pib_real'].values,
        sim_df['gdp'].values,
        years
    )
    
    # 3. OFERTA DE AGUA
    print_variable_table(
        "OFERTA DE AGUA (Millones m³)",
        real_df['oferta_agua_total'].values,
        sim_df['water_supply'].values,
        years
    )
    
    # 4. DEMANDA DE AGUA
    print_variable_table(
        "DEMANDA DE AGUA (Millones m³)",
        real_df['demanda_agua_total'].values,
        sim_df['water_demand'].values,
        years
    )
    
    # 5. PRODUCCIÓN DE ALIMENTOS (TOTAL)
    real_food_total = (
        real_df['prod_granos_real'] + 
        real_df['prod_hortalizas_real'] + 
        real_df['prod_frutas_real'] + 
        real_df['prod_carne_real'] + 
        real_df['prod_lacteos_real']
    ).values
    
    print_variable_table(
        "PRODUCCIÓN TOTAL DE ALIMENTOS (Toneladas)",
        real_food_total,
        sim_df['food_supply_total'].values,
        years
    )
    
    # 6. EMISIONES CO2
    print_variable_table(
        "EMISIONES CO2 (Megatoneladas)",
        real_df['emisiones_co2_real'].values,
        sim_df['total_co2'].values,
        years
    )
    
    print("\n✅ Validación completa terminada.\n")

if __name__ == "__main__":
    main()

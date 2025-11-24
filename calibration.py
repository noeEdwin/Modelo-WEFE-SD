
import pandas as pd
import psycopg2
from config import DB_CONFIG
from wefe_model import WEFEModel
import json
import matplotlib.pyplot as plt

def get_historical_data():
    """Obtiene los datos históricos de la base de datos"""
    conn = psycopg2.connect(**DB_CONFIG)
    query = "SELECT * FROM validacion_historica_mexico ORDER BY anio ASC"
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

def calculate_error(real, simulated):
    """
    Calcula el error relativo porcentual (MAPE)
    Fórmula: (|Real - Simulado| / Real) * 100
    """
    if real == 0:
        return 0
    return (abs(real - simulated) / real) * 100

def run_calibration():
    print("🚀 Iniciando calibración del modelo WEFE...")
    
    # 1. Cargar configuración
    with open('config_mexico_2005.json', 'r') as f:
        config = json.load(f)
    
    # 2. Obtener datos históricos
    print("📊 Obteniendo datos históricos de la BD...")
    df_real = get_historical_data()
    
    # 3. Ejecutar simulación (2005-2020)
    print("🔄 Ejecutando simulación (2005-2020)...")
    model = WEFEModel(
        initial_data=config['initial_data'],
        params=config['params'],
        scenarios=config['scenarios']
    )
    df_sim = model.run(years=16) # 2005 a 2020 son 16 años
    
    # 4. Comparar y calcular errores
    print("\n📈 RESULTADOS DE CALIBRACIÓN (MAPE %):")
    print("="*100)
    print(f"{'Variable':<25} | {'Error Promedio (%)':<20} | {'2005 (Real vs Sim)':<30} | {'2020 (Real vs Sim)':<30}")
    print("="*100)
    
    variables_map = {
        'poblacion_real': 'population',
        'pib_real': 'gdp',
        'oferta_agua_total': 'water_supply',
        'demanda_agua_total': 'water_demand',
        'prod_granos_real': 'food_production', # Nota: El modelo agrupa alimentos, esto es una aproximación si el modelo no desglosa
        'consumo_energia_real': 'energy_demand',
        'emisiones_co2_real': 'total_co2'
    }
    
    # Ajuste para alimentos: El modelo actual parece tener 'food_production' como total.
    # Sumamos las producciones reales para comparar con el total del modelo si es necesario,
    # o comparamos con la variable más cercana.
    # En el modelo simple, 'food_production' suele ser un agregado.
    # Vamos a crear una columna de 'alimentos_total_real' sumando las categorías agrícolas
    df_real['alimentos_total_real'] = (
        df_real['prod_granos_real'] + 
        df_real['prod_hortalizas_real'] + 
        df_real['prod_frutas_real'] + 
        df_real['prod_carne_real'] + 
        df_real['prod_lacteos_real']
    )
    variables_map['alimentos_total_real'] = 'food_supply_total'
    del variables_map['prod_granos_real'] # Usamos el total
    
    total_error = 0
    count = 0
    
    for real_col, sim_col in variables_map.items():
        if sim_col not in df_sim.columns:
            continue
            
        errors = []
        for i in range(len(df_real)):
            real_val = df_real.iloc[i][real_col]
            # Asegurar que comparamos el mismo año
            year = df_real.iloc[i]['anio']
            sim_row = df_sim[df_sim['year'] == year]
            
            if not sim_row.empty:
                sim_val = sim_row.iloc[0][sim_col]
                error = calculate_error(real_val, sim_val)
                errors.append(error)
        
        avg_error = sum(errors) / len(errors)
        total_error += avg_error
        count += 1
        
        # Valores inicio y fin para mostrar
        val_2005_real = df_real.iloc[0][real_col]
        val_2005_sim = df_sim[df_sim['year'] == 2005].iloc[0][sim_col]
        
        val_2020_real = df_real.iloc[-1][real_col]
        val_2020_sim = df_sim[df_sim['year'] == 2020].iloc[0][sim_col]
        
        print(f"{real_col:<25} | {avg_error:>18.2f}% | {val_2005_real:,.0f} vs {val_2005_sim:,.0f} | {val_2020_real:,.0f} vs {val_2020_sim:,.0f}")

    print("="*100)
    print(f"ERROR PROMEDIO GLOBAL DEL MODELO: {total_error/count:.2f}%")
    
    # Generar gráfica de validación
    plt.figure(figsize=(12, 8))
    
    # Ejemplo: Gráfica de Población
    plt.subplot(2, 2, 1)
    plt.plot(df_real['anio'], df_real['poblacion_real'], 'o-', label='Real')
    plt.plot(df_sim['year'], df_sim['population'], '--', label='Simulado')
    plt.title('Población')
    plt.legend()
    
    # Ejemplo: Gráfica de Agua
    plt.subplot(2, 2, 2)
    plt.plot(df_real['anio'], df_real['demanda_agua_total'], 'o-', label='Demanda Real')
    plt.plot(df_sim['year'], df_sim['water_demand'], '--', label='Demanda Simulado')
    plt.title('Demanda de Agua')
    plt.legend()

    # Ejemplo: Alimentos
    plt.subplot(2, 2, 3)
    plt.plot(df_real['anio'], df_real['alimentos_total_real'], 'o-', label='Prod. Alimentos Real')
    plt.plot(df_sim['year'], df_sim['food_supply_total'], '--', label='Prod. Alimentos Simulado')
    plt.title('Producción de Alimentos')
    plt.legend()
    
    # Ejemplo: CO2
    plt.subplot(2, 2, 4)
    plt.plot(df_real['anio'], df_real['emisiones_co2_real'], 'o-', label='CO2 Real')
    plt.plot(df_sim['year'], df_sim['total_co2'], '--', label='CO2 Simulado')
    plt.title('Emisiones CO2')
    plt.legend()
    
    plt.tight_layout()
    plt.savefig('calibracion_validacion.png')
    print("\n✅ Gráfica de validación guardada como 'calibracion_validacion.png'")

if __name__ == "__main__":
    run_calibration()

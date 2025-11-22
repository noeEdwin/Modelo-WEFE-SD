import json
import pandas as pd
import matplotlib.pyplot as plt
from wefe_model import WEFEModel
import matplotlib.ticker as ticker # Agrega esto arriba con los imports

def imprimir_resumen_amigable(df):
    """
    Imprime una tabla limpia en la consola con las variables clave.
    """
    print("\n" + "="*80)
    print(f"{'AÑO':<6} | {'AGUA (Oferta/Demanda)':<25} | {'ALIMENTOS (Ratio)':<18} | {'CO2 (Ton)':<15}")
    print("="*80)

    # Iteramos sobre las filas del DataFrame
    for index, row in df.iterrows():
        year = int(row['year'])
        
        # Formateamos números: 
        # {:,.0f} pone comas de miles y 0 decimales
        # {:,.2f} pone 2 decimales
        agua_info = f"{row['water_supply']:,.0f} / {row['water_demand']:,.0f}"
        alimentos_ratio = f"{row['food_ratio']:.2f} (Seguridad)"
        co2_info = f"{row['total_co2']:,.0f}"

        print(f"{year:<6} | {agua_info:<25} | {alimentos_ratio:<18} | {co2_info:<15}")
    
    print("="*80 + "\n")

def graficar_resultados(df):
    """
    Genera gráficas forzando el eje X a mostrar solo los años simulados.
    """
    # Aseguramos que el año sea entero para que la gráfica no se confunda
    df['year'] = df['year'].astype(int)
    
    # Filtrar el DataFrame para incluir solo los años entre 2005 y 2040
    df_filtered = df[(df['year'] >= 2005) & (df['year'] <= 2040)]

    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(10, 12))

    # --- GRÁFICA 1: AGUA ---
    ax1.set_title('Subsistema AGUA: Oferta vs Demanda')
    ax1.plot(df_filtered['year'], df_filtered['water_demand'], label='Demanda (Calculada)', color='red', linewidth=2)
    ax1.plot(df_filtered['year'], df_filtered['water_supply'], label='Oferta (Disponible)', color='blue', linestyle='--')
    ax1.set_ylabel('Metros Cúbicos')
    ax1.legend()
    ax1.grid(True, alpha=0.3)

    # --- GRÁFICA 2: ALIMENTOS ---
    ax2.set_title('Subsistema ALIMENTOS: Seguridad (>1 es bueno)')
    ax2.plot(df_filtered['year'], df_filtered['food_ratio'], color='green', linewidth=2)
    ax2.axhline(y=1.0, color='black', linestyle=':', label='Límite Escasez')
    ax2.set_ylabel('Ratio')
    ax2.legend()
    ax2.grid(True, alpha=0.3)

    # --- GRÁFICA 3: CO2 ---
    ax3.set_title('Subsistema ECOLOGÍA: Emisiones CO2')
    ax3.plot(df_filtered['year'], df_filtered['total_co2'], color='gray', linewidth=2)
    ax3.set_ylabel('Toneladas CO2')
    ax3.set_xlabel('Año de Simulación')
    ax3.grid(True, alpha=0.3)

    # --- EL TRUCO FINAL: FORZAR EL EJE X ---
    # Esto obliga a la gráfica a empezar exactamente en el primer año y terminar en el último
    for ax in [ax1, ax2, ax3]:
        ax.set_xlim(2005, 2040)  # Limitar el eje X a 2005-2040
        ax.xaxis.set_major_locator(ticker.MaxNLocator(integer=True))  # Solo años enteros

    plt.tight_layout()
    plt.tight_layout()
    plt.savefig('resultados_mexico_2005.png')
    print("✅ Gráfica guardada como 'resultados_mexico_2005.png'")

# --- BLOQUE PRINCIPAL ---

if __name__ == "__main__":
    try:
        # 1. Cargar configuración
        print("Cargando 'config_mexico_2005.json'...")
        with open('config_mexico_2005.json', 'r') as file:
            config = json.load(file)

        # 2. Inicializar Modelo
        print("Inicializando modelo WEFE...")
        modelo = WEFEModel(
            initial_data=config['initial_data'],
            params=config['params'],
            scenarios=config['scenarios']
        )

        # 3. Correr Simulación (15 años: 2005 -> 2020)
        print("Ejecutando simulación de 15 años...")
        resultados = modelo.run(years=30)
        # 4. Mostrar resultados amigables
        imprimir_resumen_amigable(resultados)
        
        # 5. Graficar (Opcional, abre una ventana)
        graficar_resultados(resultados)

    except FileNotFoundError:
        print("❌ Error: No se encontró el archivo 'config_mexico_2005.json'. Asegúrate de que esté en la misma carpeta.")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
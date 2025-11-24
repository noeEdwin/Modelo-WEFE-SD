import json
from wefe_model import WEFEModel

# Cargar configuración
with open('config_mexico_2005.json', 'r') as f:
    config = json.load(f)

# Crear modelo
modelo = WEFEModel(
    initial_data=config['initial_data'],
    params=config['params'],
    scenarios=config['scenarios']
)

# Simular 16 años (2005-2020)
resultados = modelo.run(years=16)

# Datos reales de oferta de energía (Oferta interna bruta)
real_data = [7093.954, 7160.402, 7017.244, 7094.742, 7292.225, 6923.625, 7033.632, 
             6994.956, 7207.587, 6812.267, 6403.126, 5906.558, 5536.158, 4895.142, 
             4675.041, 4276.316]

print("="*80)
print("CALIBRACIÓN - OFERTA DE ENERGÍA")
print("="*80)
print(f"{'Año':<6} | {'Real (PJ)':<15} | {'Simulado (PJ)':<15} | {'Diferencia':<15} | {'Error %':<10}")
print("-"*80)

errors = []
for i, year in enumerate(range(2005, 2021)):
    real = real_data[i]
    sim = resultados['energy_supply'].values[i]
    diff = sim - real
    error_pct = abs(diff / real) * 100
    errors.append(error_pct)
    
    print(f"{year:<6} | {real:<15,.2f} | {sim:<15,.2f} | {diff:<15,.2f} | {error_pct:<9.2f}%")

avg_error = sum(errors) / len(errors)
print("-"*80)
print(f"ERROR PROMEDIO (MAPE): {avg_error:.2f}%")
print("="*80)

# Verificar tendencia
print(f"\nOferta 2005: {resultados['energy_supply'].values[0]:.2f} PJ")
print(f"Oferta 2020: {resultados['energy_supply'].values[-1]:.2f} PJ")
print(f"Cambio simulado: {((resultados['energy_supply'].values[-1] / resultados['energy_supply'].values[0]) - 1) * 100:.2f}%")
print(f"Cambio real: {((real_data[-1] / real_data[0]) - 1) * 100:.2f}%")

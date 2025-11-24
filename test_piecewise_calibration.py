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

print("="*90)
print("CALIBRACIÓN REFINADA - OFERTA DE ENERGÍA (Modelo Piecewise)")
print("="*90)
print(f"{'Año':<6} | {'Real (PJ)':<15} | {'Simulado (PJ)':<15} | {'Diferencia':<15} | {'Error %':<10} | {'Período':<10}")
print("-"*90)

errors = []
errors_period1 = []
errors_period2 = []

for i, year in enumerate(range(2005, 2021)):
    real = real_data[i]
    sim = resultados['energy_supply'].values[i]
    diff = sim - real
    error_pct = abs(diff / real) * 100
    errors.append(error_pct)
    
    period = "Estable" if year <= 2013 else "Declive"
    if year <= 2013:
        errors_period1.append(error_pct)
    else:
        errors_period2.append(error_pct)
    
    print(f"{year:<6} | {real:<15,.2f} | {sim:<15,.2f} | {diff:<15,.2f} | {error_pct:<9.2f}% | {period:<10}")

avg_error = sum(errors) / len(errors)
avg_error_p1 = sum(errors_period1) / len(errors_period1) if errors_period1 else 0
avg_error_p2 = sum(errors_period2) / len(errors_period2) if errors_period2 else 0

print("-"*90)
print(f"ERROR PROMEDIO TOTAL (MAPE): {avg_error:.2f}%")
print(f"ERROR PROMEDIO Período 1 (2005-2013): {avg_error_p1:.2f}%")
print(f"ERROR PROMEDIO Período 2 (2014-2020): {avg_error_p2:.2f}%")
print("="*90)

# Verificar tendencia
print(f"\n📊 COMPARACIÓN DE TENDENCIAS")
print(f"{'Métrica':<40} | {'Real':<15} | {'Simulado':<15}")
print("-"*75)
print(f"{'Oferta 2005 (PJ)':<40} | {real_data[0]:<15,.2f} | {resultados['energy_supply'].values[0]:<15,.2f}")
print(f"{'Oferta 2020 (PJ)':<40} | {real_data[-1]:<15,.2f} | {resultados['energy_supply'].values[-1]:<15,.2f}")
print(f"{'Cambio total 2005-2020 (%)':<40} | {((real_data[-1] / real_data[0]) - 1) * 100:<15,.2f} | {((resultados['energy_supply'].values[-1] / resultados['energy_supply'].values[0]) - 1) * 100:<15,.2f}")
print(f"{'Oferta 2013 (PJ)':<40} | {real_data[8]:<15,.2f} | {resultados['energy_supply'].values[8]:<15,.2f}")
print(f"{'Cambio 2005-2013 (%)':<40} | {((real_data[8] / real_data[0]) - 1) * 100:<15,.2f} | {((resultados['energy_supply'].values[8] / resultados['energy_supply'].values[0]) - 1) * 100:<15,.2f}")
print(f"{'Cambio 2013-2020 (%)':<40} | {((real_data[-1] / real_data[8]) - 1) * 100:<15,.2f} | {((resultados['energy_supply'].values[-1] / resultados['energy_supply'].values[8]) - 1) * 100:<15,.2f}")
print("="*75)

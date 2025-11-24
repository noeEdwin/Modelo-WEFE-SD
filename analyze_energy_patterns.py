import json

# Datos reales de oferta de energía
real_data = [7093.954, 7160.402, 7017.244, 7094.742, 7292.225, 6923.625, 7033.632, 
             6994.956, 7207.587, 6812.267, 6403.126, 5906.558, 5536.158, 4895.142, 
             4675.041, 4276.316]
years = list(range(2005, 2021))

print("="*80)
print("ANÁLISIS DETALLADO - OFERTA DE ENERGÍA")
print("="*80)

# Calcular tasas anuales
print("\nTasas de crecimiento año por año:")
print(f"{'Año':<6} | {'Valor (PJ)':<12} | {'Cambio %':<10}")
print("-"*40)
growth_rates = []
for i in range(len(real_data)):
    if i == 0:
        print(f"{years[i]:<6} | {real_data[i]:<12,.2f} | {'BASE':<10}")
    else:
        growth = ((real_data[i] - real_data[i-1]) / real_data[i-1]) * 100
        growth_rates.append(growth)
        print(f"{years[i]:<6} | {real_data[i]:<12,.2f} | {growth:+10.2f}%")

# Analizar por períodos
print("\n" + "="*80)
print("ANÁLISIS POR PERÍODOS")
print("="*80)

# Período 1: 2005-2013 (antes de la reforma energética)
period1_data = real_data[0:9]  # 2005-2013
period1_growth = []
for i in range(1, len(period1_data)):
    g = ((period1_data[i] - period1_data[i-1]) / period1_data[i-1])
    period1_growth.append(g)

avg_growth_period1 = sum(period1_growth) / len(period1_growth)
total_change_period1 = ((period1_data[-1] - period1_data[0]) / period1_data[0])

print(f"\nPeríodo 1 (2005-2013):")
print(f"  Tasa promedio anual: {avg_growth_period1*100:+.2f}%")
print(f"  Cambio total: {total_change_period1*100:+.2f}%")
print(f"  Inicio: {period1_data[0]:.2f} PJ")
print(f"  Fin: {period1_data[-1]:.2f} PJ")

# Período 2: 2013-2020 (reforma energética y caída acelerada)
period2_data = real_data[8:]  # 2013-2020
period2_growth = []
for i in range(1, len(period2_data)):
    g = ((period2_data[i] - period2_data[i-1]) / period2_data[i-1])
    period2_growth.append(g)

avg_growth_period2 = sum(period2_growth) / len(period2_growth)
total_change_period2 = ((period2_data[-1] - period2_data[0]) / period2_data[0])

print(f"\nPeríodo 2 (2013-2020):")
print(f"  Tasa promedio anual: {avg_growth_period2*100:+.2f}%")
print(f"  Cambio total: {total_change_period2*100:+.2f}%")
print(f"  Inicio: {period2_data[0]:.2f} PJ")
print(f"  Fin: {period2_data[-1]:.2f} PJ")

# Probar ajuste con valor inicial diferente
print("\n" + "="*80)
print("PRUEBA DE AJUSTE DE VALOR INICIAL")
print("="*80)

# El valor actual en config es 7093.954, pero podríamos necesitar un ajuste
# para compensar las renovables que se suman después
config_value = 7093.954
print(f"Valor actual en config: {config_value:.2f} PJ")
print(f"Valor real 2005: {real_data[0]:.2f} PJ")

# Calcular qué valor inicial daría mejor ajuste con -3.22% anual
target_2020 = real_data[-1]
growth_rate = -0.0322
years_elapsed = 15

# Fórmula: final = initial * (1 + rate)^years
# initial = final / (1 + rate)^years
required_initial = target_2020 / ((1 + growth_rate) ** years_elapsed)
print(f"\nValor inicial requerido para alcanzar {target_2020:.2f} en 2020: {required_initial:.2f} PJ")
print(f"Ajuste necesario: {required_initial - config_value:+.2f} PJ ({((required_initial/config_value)-1)*100:+.2f}%)")

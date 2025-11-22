# Documentación del Modelo WEFE (Water-Energy-Food-Ecology)

Este documento detalla la implementación del modelo de Dinámica de Sistemas WEFE en el archivo `wefe_model.py`, relacionando directamente el código con las ecuaciones teóricas del artículo de referencia (Ling et al., Ecological Indicators 158, 2024).

## 1. Subsistema de Agua (Water Subsystem)

El subsistema de agua calcula la demanda y la oferta para determinar el índice de estrés hídrico o balance ($W_R$).

### Demanda de Agua ($WD$)
**Ecuación Teórica (1):**
$$WD = WD_{agriculture} + WD_{industry} + WD_{domestic} + WD_{ecology} + WD_{energy}$$

**Implementación en Código (`_step_water`):**
El código calcula la **Demanda Humana Consuntiva** separada de la demanda ecológica.
```python
# Líneas 87-99
wd_agri = (s['area_grains'] + s['area_veggies'] + s['area_fruits']) * p['quota_water_crop']
wd_ind = s['gdp'] * p['quota_water_ind']
wd_dom = s['population'] * p['quota_water_dom']
wd_energy = s['energy_production_total'] * p['quota_water_energy']

wd_human = wd_agri + wd_ind + wd_dom + wd_energy
```
*Nota:* A diferencia de la Ecuación 1, el código trata la demanda ecológica ($WD_{ecology}$) como una restricción a la oferta disponible, no como un componente de la demanda consuntiva sumada.

### Componentes de Demanda
*   **Agricultura (Eq. 2):** $\sum (S_i \times WQ_{food-i})$
    *   *Código:* Se simplifica usando una cuota promedio `quota_water_crop` multiplicada por el área total de cultivos (granos, vegetales, frutas).
*   **Industria (Eq. 3):** $GDP \times WQ_{secondary}$
    *   *Código:* `s['gdp'] * p['quota_water_ind']`
*   **Doméstico (Eq. 4):** $P \times WQ_{domestic}$
    *   *Código:* `s['population'] * p['quota_water_dom']`
*   **Energía (Eq. 5):** $\sum (ES_e \times WQ_{energy-e})$
    *   *Código:* `s['energy_production_total'] * p['quota_water_energy']` (Simplificación: usa producción total y un factor promedio).

### Oferta y Balance ($WS$ y $W_R$)
**Ecuaciones Teóricas (6 y 7):**
$$WS = WS_{surface} + WS_{ground} + WS_{unconventional}$$
$$W_R = \frac{WS}{WD}$$

**Implementación en Código:**
```python
# Líneas 107-114
total_ws_natural = s['ws_surface'] + s['ws_ground'] + s['ws_unconventional'] # Eq 6

# Ajuste por caudal ecológico (diferencia con Eq 7 estricta)
ws_available = total_ws_natural - wd_eco 

w_r = ws_available / wd_human # Eq 7 adaptada
```
*Interpretación:* El balance $W_R$ se calcula como la oferta *disponible* (después de restar el requerimiento ecológico) dividida entre la demanda humana.

---

## 2. Subsistema de Energía (Energy Subsystem)

### Demanda de Energía ($ED$)
**Ecuación Teórica (8):**
$$ED = ED_{food} + ED_{industry} + ED_{other} + ED_{domestic} + ED_{water}$$

**Implementación en Código (`_step_energy`):**
```python
# Línea 141
total_ed = ed_ind + ed_dom + ed_water + ed_agri
```
*   **Industria (Eq. 10):** `s['gdp'] * p['intensity_energy_ind']`
*   **Doméstico (Eq. 11):** `s['population'] * p['intensity_energy_dom']`
*   **Agua (Eq. 12):** `water_metrics['water_demand'] * p['energy_per_m3_water']`
*   **Alimentos (Eq. 9):** `food_metrics['food_supply_total'] * p.get('energy_intensity_agri', 0)`

### Oferta de Energía ($ES$)
**Ecuaciones Teóricas (13 y 14):**
$$ES = ES_{coal} + ES_{oil} + ES_{gas} + ES_{news} + ES_{food}$$
$$ES_{food} = FS_c \times standard$$

**Implementación en Código:**
El código calcula la bioenergía ($ES_{food}$) basándose en la producción de granos:
```python
# Línea 147 (Eq 14)
bioenergy = food_metrics['production_grains'] * p.get('straw_energy_factor', 0)
supply_renewables = s['es_renewables'] + bioenergy
```
Posteriormente, calcula el déficit energético y lo cubre con combustibles fósiles (Carbón, Petróleo, Gas) manteniendo los ratios del año base (Líneas 156-164), cumpliendo con la suma de la Ecuación 13.

### Balance Energético ($E_R$)
**Ecuación Teórica (15):**
$$E_R = \frac{ES}{ED}$$

**Implementación en Código:**
```python
# Línea 175
e_r = total_es / total_ed
```

---

## 3. Subsistema de Alimentos (Food Subsystem)

### Demanda de Alimentos ($FD$)
**Ecuaciones Teóricas (16 y 17):**
$$FD = FD_c + FD_v + FD_f + FD_m + FD_e$$
$$FD_{type} = P \times FD_{per-i}$$

**Implementación en Código (`_step_food`):**
El código calcula la demanda humana directa multiplicando la población por la dieta per cápita (Eq. 17).
```python
# Líneas 37-41
fd_grains_human = s['population'] * p['diet_grains_per_capita']
# ... (vegetales, frutas, carne, lácteos)
```
*Adición Importante:* El código agrega explícitamente la **Demanda de Forraje** (Feed Demand) para el ganado, que es un componente indirecto de la demanda de granos necesario para sostener la producción de carne y lácteos (Líneas 43-57).

### Oferta de Alimentos ($FS$)
**Ecuaciones Teóricas (18 y 19):**
$$FS = \sum FS_{type}$$
$$FS_{type} = S_{type} \times yield_{type}$$

**Implementación en Código:**
```python
# Líneas 62-66 (Eq 19)
fs_grains = s['area_grains'] * s['yield_grains']
# ... (otros cultivos)

# Línea 68 (Eq 18)
total_fs = fs_grains + fs_veggies + fs_fruits + fs_meat + fs_dairy
```

### Balance Alimentario ($F_R$)
**Ecuación Teórica (20):**
$$F_R = \frac{FS}{FD}$$

**Implementación en Código:**
```python
# Línea 73
'food_ratio': total_fs / total_fd
```

---

## 4. Subsistema de Ecología (Ecology Subsystem)

### Emisiones de CO2
**Ecuaciones Teóricas (23 y 24):**
$$CO_2 = CO_{2coal} + CO_{2oil} + CO_{2gas}$$
$$CO_{2source} = ED_{source} \times EF_{source}$$

**Implementación en Código (`_step_ecology`):**
```python
# Líneas 209-213
co2_coal = energy_metrics['consumption_coal'] * p['emission_factor_coal']
co2_oil = energy_metrics['consumption_oil'] * p['emission_factor_oil']
co2_gas = energy_metrics['consumption_gas'] * p.get('emission_factor_gas', 0)

total_co2 = co2_coal + co2_oil + co2_gas
```

### Demanda Química de Oxígeno (COD)
**Ecuaciones Teóricas (21 y 22):**
$$COD = COD_{agri} + COD_{ind} + COD_{dom} + COD_{facilities}$$
$$COD_{dom} = WW_{dom} \times C_{dom}$$

**Implementación en Código:**
El código implementa principalmente el **COD Doméstico**:
```python
# Líneas 217-218
wastewater = (s['population'] * p['quota_water_dom']) * 0.8 # Factor de retorno 0.8
total_cod = wastewater * p['pollutant_concentration_dom']
```
*Nota:* Las emisiones de COD agrícola e industrial no están explícitamente desglosadas en esta versión del código, enfocándose en el impacto urbano/doméstico.

---

## 5. Subsistema Económico y Social
El modelo actualiza las variables conductoras (Drivers) al inicio de cada paso de simulación (`_calculate_social_economic`), basándose en las tasas de crecimiento definidas en los escenarios (Table 1 del artículo).

```python
# Líneas 24-26
self.state['population'] *= (1 + self.scenarios.get('growth_pop', 0))
self.state['gdp'] *= (1 + self.scenarios.get('growth_gdp', 0))
self.state['urbanization_rate'] += self.scenarios.get('growth_urbanization', 0)
```

## Resumen de Correspondencia

| Variable | Símbolo Paper | Variable en Código (`wefe_model.py`) | Ecuación Paper |
| :--- | :--- | :--- | :--- |
| Demanda Agua Total | $WD$ | `wd_human` (+ `wd_eco` como restricción) | Eq. 1 |
| Oferta Agua Total | $WS$ | `total_ws_natural` | Eq. 6 |
| Balance Agua | $W_R$ | `water_ratio` | Eq. 7 |
| Demanda Energía | $ED$ | `total_ed` | Eq. 8 |
| Oferta Energía | $ES$ | `total_es` | Eq. 13 |
| Balance Energía | $E_R$ | `energy_ratio` | Eq. 15 |
| Demanda Alimentos | $FD$ | `total_fd` | Eq. 16 |
| Oferta Alimentos | $FS$ | `total_fs` | Eq. 18 |
| Balance Alimentos | $F_R$ | `food_ratio` | Eq. 20 |
| Emisiones CO2 | $CO_2$ | `total_co2` | Eq. 23 |

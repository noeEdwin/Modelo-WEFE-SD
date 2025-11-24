# Documentación Matemática Detallada: Modelo WEFE-SD

Este documento contiene las derivaciones matemáticas completas y explicaciones ecuación por ecuación del modelo WEFE (Agua-Energía-Alimentos-Ecología) implementado en `wefe_model.py`.

Para la documentación general del proyecto, consulta [`README.md`](file:///home/edwinnoe/SIMULACION_PROYECTO/README.md).

> [!NOTE]
> **Referencias de Líneas de Código:** Los números de línea mencionados en este documento son aproximados y pueden variar ligeramente con actualizaciones del código. Las referencias a funciones (ej. `_step_water`, `_step_food`) son precisas y permanentes.

---

## 📐 Tabla de Contenidos

1. [Subsistema de Agua (Ecuaciones 1-7)](#subsistema-de-agua)
2. [Subsistema de Energía (Ecuaciones 8-15)](#subsistema-de-energía)
3. [Subsistema de Alimentos (Ecuaciones 16-20)](#subsistema-de-alimentos)
4. [Subsistema de Ecología (Ecuaciones 21-24)](#subsistema-de-ecología)
5. [Validación del Modelo (Ecuación 25)](#validación-del-modelo)

---

## Subsistema de Agua

### Ecuación 1: Demanda Total de Agua

**Ecuación:**
$$WD = WD_{agri} + WD_{ind} + WD_{dom} + WD_{energy} + WD_{eco}$$

**Variables:**
- $WD$ = Demanda total de agua (hm³/año)
- $WD_{agri}$ = Demanda agrícola
- $WD_{ind}$ = Demanda industrial
- $WD_{dom}$ = Demanda doméstica
- $WD_{energy}$ = Demanda del sector energético
- $WD_{eco}$ = Requerimiento ecológico (caudal ecológico)

**Derivación:**
El agua en un país se consume en múltiples sectores simultáneamente. Para conocer la presión total sobre los recursos hídricos, sumamos todas las demandas sectoriales.

**Implementación (`wefe_model.py`, líneas 87-115):**
```python
# Línea 87-96: Cálculo de cada componente
wd_agri = (s['area_grains'] + s['area_veggies'] + s['area_fruits']) * p['quota_water_crop']
wd_ind = s['gdp'] * p['quota_water_ind']
wd_dom = s['population'] * p['quota_water_dom']
wd_energy = s['energy_production_total'] * p['quota_water_energy']

# Línea 108: Suma de demanda humana (sin eco)
wd_human = (wd_agri + wd_ind + wd_dom + wd_energy) / 1000000.0

# Línea 112: Agregamos demanda ecológica
wd_eco = s.get('wd_eco_req', 0)
wd_total = wd_human + wd_eco
```

**Nota:** En el código, separamos `wd_human` (consumo humano) de `wd_eco` (requerimiento ecológico) para poder reportarlos por separado. Sin embargo, la demanda total del sistema es la suma de ambos.

---

### Ecuación 2: Demanda Agrícola de Agua

**Ecuación:**
$$WD_{agri} = \sum_{i=1}^{n} (S_i \times WQ_i)$$

Donde:
- $S_i$ = Superficie sembrada del cultivo $i$ (hectáreas)
- $WQ_i$ = Cuota de agua por hectárea del cultivo $i$ (m³/ha)

**Derivación:**
Cada hectárea de tierra cultivada requiere una cantidad específica de agua para riego. La demanda total agrícola es simplemente el área total multiplicada por el requerimiento hídrico promedio.

**Implementación (`wefe_model.py`, líneas 87-89):**
```python
# Sumamos todas las áreas de cultivo
total_area = s['area_grains'] + s['area_veggies'] + s['area_fruits']

# Multiplicamos por la cuota promedio de agua
wd_agri = total_area * p['quota_water_crop']
```

**Ejemplo Numérico (2005):**
- Granos: 11,690,244 ha
- Hortalizas: 514,984 ha  
- Frutas: 1,418,629 ha
- **Total:** 13,623,857 ha
- Cuota promedio: 4,660.4 m³/ha
- **Resultado:** 63,500 millones de m³

---

### Ecuación 3: Demanda Industrial de Agua

**Ecuación:**
$$WD_{ind} = GDP \times WQ_{sec}$$

Donde:
- $GDP$ = Producto Interno Bruto (pesos MXN)
- $WQ_{sec}$ = Intensidad de uso de agua industrial (m³/peso)

**Derivación:**
La actividad económica (medida por el PIB) está directamente correlacionada con el consumo de agua industrial. A mayor producción industrial, mayor enfriamiento de maquinaria, procesamiento, limpieza, etc.

**Implementación (`wefe_model.py`, línea 90):**
```python
wd_ind = s['gdp'] * p['quota_water_ind']
```

**Ejemplo Numérico (2005):**
- PIB: 18,929,250,872,000 pesos
- Intensidad: 0.00015125 m³/peso
- **Resultado:** 2,863 millones de m³

**Nota:** La intensidad parece pequeña porque el PIB está en unidades individuales de pesos. El valor de `quota_water_ind` fue calibrado dividiendo el consumo industrial real entre el PIB.

---

### Ecuación 4: Demanda Doméstica de Agua

**Ecuación:**
$$WD_{dom} = P \times WQ_{dom}$$

Donde:
- $P$ = Población total (habitantes)
- $WQ_{dom}$ = Cuota per cápita de agua doméstica (m³/persona·año)

**Derivación:**
Cada persona consume agua para beber, cocinar, higiene, y otros usos domésticos. La demanda total es simplemente población por consumo promedio.

**Implementación (`wefe_model.py`, línea 93):**
```python
wd_dom = s['population'] * p['quota_water_dom']
```

**Ejemplo Numérico (2005):**
- Población: 103,263,388 habitantes
- Cuota per cápita: 103.65 m³/persona·año
- **Resultado:** 10,703 millones de m³

---

### Ecuación 5: Demanda de Agua del Sector Energético

**Ecuación:**
$$WD_{energy} = \sum_{j=1}^{m} (ES_j \times WQ_{e,j})$$

Donde:
- $ES_j$ = Energía producida por la fuente $j$ (PJ)
- $WQ_{e,j}$ = Intensidad de agua para generar energía (m³/PJ)

**Derivación:**
Las plantas de generación eléctrica (especialmente termoeléctricas) requieren agua para enfriamiento. A mayor generación de energía, mayor consumo de agua.

**Implementación (`wefe_model.py`, línea 96):**
```python
wd_energy = s['energy_production_total'] * p['quota_water_energy']
```

**Ejemplo Numérico (2005):**
- Energía total: 7,093.954 PJ
- Intensidad: 594,952 m³/PJ
- **Resultado:** 4,220 millones de m³

---

### Ecuación 6: Oferta Total de Agua

**Ecuación:**
$$WS = WS_{sup} + WS_{sub} + WS_{un}$$

Donde:
- $WS$ = Oferta total (disponibilidad natural) (hm³)
- $WS_{sup}$ = Agua superficial (ríos, lagos) (hm³)
- $WS_{sub}$ = Agua subterránea (acuíferos) (hm³)
- $WS_{un}$ = Agua no convencional (desalinización, reúso) (hm³)

**Derivación:**
La oferta de agua proviene de múltiples fuentes. La suma nos da la disponibilidad total que el país puede usar.

**Implementación (`wefe_model.py`, línea 119):**
```python
total_ws_natural = s['ws_surface'] + s['ws_ground'] + s['ws_unconventional']
```

**Ejemplo Numérico (2005):**
- Superficial: 395,210 hm³
- Subterránea: 76,984 hm³
- No convencional: 835.7 hm³
- **Total:** 473,030 hm³

---

### Ecuación 7: Ratio de Estrés Hídrico

**Ecuación:**
$$W_R = \frac{WS}{WD}$$

Donde:
- $W_R$ = Ratio de estrés hídrico (adimensional)
- $WS$ = Oferta de agua
- $WD$ = Demanda de agua

**Interpretación:**
- $W_R > 1.0$: El agua disponible excede la demanda (seguro)
- $W_R = 1.0$: Balance perfecto (riesgoso)
- $W_R < 1.0$: Déficit hídrico (crisis)

**Implementación (`wefe_model.py`, línea 124):**
```python
w_r = total_ws_natural / wd_total if wd_total > 0 else 0
```

**Ejemplo Numérico (2005):**
- Oferta: 473,030 hm³
- Demanda (humana + eco): 223,089 hm³
- **Ratio:** 2.12 (Seguro, con margen)

---

## Subsistema de Energía

### Ecuación 8: Demanda Total de Energía

**Ecuación:**
$$ED = ED_{ind} + ED_{dom} + ED_{water} + ED_{food}$$

Donde:
- $ED$ = Demanda total de energía (PJ/año)
- $ED_{ind}$ = Demanda industrial
- $ED_{dom}$ = Demanda doméstica
- $ED_{water}$ = Energía para bombeo de agua
- $ED_{food}$ = Energía para agricultura (tractores, maquinaria)

**Derivación:**
Similar al agua, la energía se consume en múltiples sectores. Sumamos todas las demandas para conocer la presión total sobre el sistema energético.

**Implementación (`wefe_model.py`, línea 152):**
```python
total_ed = ed_ind + ed_dom + ed_water + ed_agri
```

---

### Ecuación 9: Demanda de Energía Agrícola

**Ecuación:**
$$ED_{food} = \sum_{i=1}^{n} (FS_i \times EI_{agri})$$

Donde:
- $FS_i$ = Producción del alimento $i$ (toneladas)
- $EI_{agri}$ = Intensidad energética agrícola (PJ/tonelada)

**Derivación:**
Producir alimentos requiere energía (diesel para tractores, electricidad para riego, etc.). A mayor producción, mayor consumo energético.

**Implementación (`wefe_model.py`, línea 150):**
```python
ed_agri = food_metrics['food_supply_total'] * p.get('energy_intensity_agri', 0)
```

**Ejemplo Numérico (2005):**
- Producción total: 70,244,775 toneladas
- Intensidad: 0.000002103 PJ/t
- **Resultado:** 147.7 PJ

---

### Ecuación 10: Demanda de Energía Industrial

**Ecuación:**
$$ED_{ind} = \sum_{k=1}^{p} (GDP \times EC_k)$$

Donde:
- $GDP$ = Producto Interno Bruto
- $EC_k$ = Coeficiente de consumo energético industrial

**Derivación:**
La industria consume energía para manufactura, procesamiento, transporte, etc. El consumo es proporcional al tamaño de la economía.

**Implementación (`wefe_model.py`, línea 143):**
```python
ed_ind = s['gdp'] * p['intensity_energy_ind']
```

---

### Ecuación 11: Demanda de Energía Doméstica

**Ecuación:**
$$ED_{dom} = P \times EC_{dom}$$

Donde:
- $P$ = Población
- $EC_{dom}$ = Consumo energético per cápita (PJ/persona)

**Derivación:**
Cada persona consume energía en iluminación, electrodomésticos, calefacción, etc.

**Implementación (`wefe_model.py`, línea 144):**
```python
ed_dom = s['population'] * p['intensity_energy_dom']
```

---

### Ecuación 12: Energía para Bombeo de Agua

**Ecuación:**
$$ED_{water} = \sum_{k=1}^{m} (WD_k \times E_{pump})$$

Donde:
- $WD_k$ = Demanda de agua del sector $k$ (m³)
- $E_{pump}$ = Energía requerida por m³ bombeado (PJ/m³)

**Derivación:**
Mover agua requiere electricidad para bombas. A mayor demanda de agua, mayor consumo eléctrico.

**Implementación (`wefe_model.py`, línea 147):**
```python
ed_water = water_metrics['water_demand'] * p['energy_per_m3_water']
```

**Ejemplo Numérico (2005):**
- Agua bombeada: 81,431 millones de m³
- Intensidad: 3.42e-9 PJ/m³
- **Resultado:** 0.278 PJ

**Nota:** Este valor parece pequeño porque representa solo el bombeo, no el tratamiento ni distribución completa.

---

### Ecuación 13: Oferta Total de Energía

**Ecuación:**
$$ES = ES_{coal} + ES_{oil} + ES_{gas} + ES_{renewables} + ES_{bio}$$

Donde:
- $ES$ = Oferta total de energía (PJ)
- $ES_{coal}$ = Energía de carbón
- $ES_{oil}$ = Energía de petróleo
- $ES_{gas}$ = Energía de gas natural
- $ES_{renewables}$ = Energía renovable (hidro, solar, eólica)
- $ES_{bio}$ = Bioenergía (residuos agrícolas)

**Derivación:**
La oferta de energía proviene de diversas fuentes. La suma total debe cubrir la demanda.

**Implementación (`wefe_model.py`, líneas 158-196):**
```python
# Primero calculamos renovables + bio
supply_renewables = s['es_renewables'] + bioenergy

# Luego calculamos el "hueco" que deben llenar los fósiles
fossil_gap = total_ed - supply_renewables

# Si hay déficit, lo llenamos con fósiles
if fossil_gap > 0:
    s['es_coal'] = fossil_gap * ratio_coal
    s['es_oil'] = fossil_gap * ratio_oil
    s['es_gas'] = fossil_gap * ratio_gas

# Oferta total
total_es = s['es_coal'] + s['es_oil'] + s['es_gas'] + supply_renewables
```

**Concepto Clave: Fossil Gap**
Esta es una innovación de nuestro modelo. En lugar de asumir que la energía simplemente "se ajusta", calculamos explícitamente cuánto fósil necesitamos quemar para cubrir la demanda que las renovables no pueden satisfacer.

---

### Ecuación 14: Bioenergía de Residuos Agrícolas

**Ecuación:**
$$ES_{bio} = FS_{grains} \times std$$

Donde:
- $FS_{grains}$ = Producción de granos (toneladas)
- $std$ = Factor de conversión de paja a energía (PJ/tonelada)

**Derivación:**
Cuando cosechas granos, generas residuos (paja). Esta paja puede quemarse para generar electricidad o calor.

**Implementación (`wefe_model.py`, línea 158):**
```python
bioenergy = food_metrics['production_grains'] * p.get('straw_energy_factor', 0)
```

**Ejemplo Numérico (2005):**
- Producción de granos: 28,000,000 toneladas (aprox)
- Factor paja: 0.000003 PJ/t
- **Bioenergía:** 84 PJ

---

### Ecuación 15: Ratio de Balance Energético

**Ecuación:**
$$E_R = \frac{ES}{ED}$$

Donde:
- $E_R$ = Ratio energético (adimensional)
- $ES$ = Oferta de energía
- $ED$ = Demanda de energía

**Interpretación:**
- $E_R > 1.0$: Superávit energético (se puede exportar)
- $E_R = 1.0$: Balance perfecto
- $E_R < 1.0$: Déficit (apagones, importaciones)

**Implementación (`wefe_model.py`, línea 200):**
```python
e_r = total_es / total_ed if total_ed > 0 else 0
```

---

## Subsistema de Alimentos

### Ecuación 16: Demanda Total de Alimentos

**Ecuación:**
$$FD = FD_{human} + FD_{feed}$$

Donde:
- $FD$ = Demanda total de alimentos (toneladas)
- $FD_{human}$ = Demanda humana directa
- $FD_{feed}$ = Demanda para alimentar ganado

**Derivación:**
Los granos no solo alimentan humanos. Una gran parte se destina a alimentar vacas, cerdos y pollos. Si ignoramos esto, subestimaríamos masivamente la demanda agrícola.

**Implementación (`wefe_model.py`, líneas 46-68):**
```python
# Demanda humana directa
fd_grains_human = s['population'] * p['diet_grains_per_capita']
fd_veggies = s['population'] * p['diet_veggies_per_capita']
fd_fruits = s['population'] * p['diet_fruits_per_capita']
fd_meat = s['population'] * (p['diet_red_meat_per_capita'] + p['diet_white_meat_per_capita'])
fd_dairy = s['population'] * p['diet_dairy_per_capita']

# Demanda ganadera (feed)
factor_feed_meat = 3.5  # kg grano / kg carne
factor_feed_dairy = 1.2  # kg grano / kg lácteo
fd_feed_meat = fd_meat * factor_feed_meat
fd_feed_dairy = fd_dairy * factor_feed_dairy
total_feed_demand = fd_feed_meat + fd_feed_dairy

# Granos totales = humanos + ganado
fd_grains_total = fd_grains_human + total_feed_demand

# Demanda total
total_fd = fd_grains_total + fd_veggies + fd_fruits + fd_meat + fd_dairy
```

**Ejemplo Numérico (2005):**
- Demanda humana de carne: 5 millones de toneladas
- Factor de conversión: 3.5 kg grano/kg carne
- **Demanda de granos para ganado:** 17.5 millones de toneladas
- Demanda humana directa de granos: 14 millones de toneladas
- **Total granos:** 31.5 millones de toneladas

**Concepto Clave:**
Sin contabilizar el feed, pensaríamos que solo necesitamos 14 Mt de granos, cuando en realidad necesitamos 31.5 Mt. Esto explica por qué México importa tanto maíz a pesar de ser productor.

---

### Ecuación 17: Demanda Humana de Alimentos

**Ecuación:**
$$FD_{human} = \sum_{i=1}^{n} (P \times diet_i)$$

Donde:
- $P$ = Población
- $diet_i$ = Consumo per cápita del alimento $i$ (kg/persona·año)

**Implementación:** Ver ecuación 16 arriba (líneas 46-50).

---

### Ecuación 18: Oferta Total de Alimentos

**Ecuación:**
$$FS = FS_{grains} + FS_{veggies} + FS_{fruits} + FS_{meat} + FS_{dairy}$$

**Implementación (`wefe_model.py`, línea 77):**
```python
total_fs = fs_grains + fs_veggies + fs_fruits + fs_meat + fs_dairy
```

---

### Ecuación 19: Producción por Rendimiento

**Ecuación:**
$$FS_i = S_i \times Y_i$$

Donde:
- $FS_i$ = Producción del alimento $i$ (toneladas)
- $S_i$ = Área sembrada o inventario ganadero
- $Y_i$ = Rendimiento (toneladas/hectárea o toneladas/cabeza)

**Implementación (`wefe_model.py`, líneas 71-75):**
```python
fs_grains = s['area_grains'] * s['yield_grains']
fs_veggies = s['area_veggies'] * s['yield_veggies']
fs_fruits = s['area_fruits'] * s['yield_fruits']
fs_meat = (s['heads_cows'] * s['yield_meat']) + (s['heads_poultry'] * s['yield_poultry'])
fs_dairy = s['heads_dairy'] * s['yield_dairy']
```

**Ejemplo Numérico (2005):**
- Área de granos: 11,690,244 ha
- Rendimiento: 2.395 t/ha
- **Producción:** 28,000,000 toneladas

---

### Ecuación 20: Ratio de Seguridad Alimentaria

**Ecuación:**
$$F_R = \frac{FS}{FD}$$

Donde:
- $F_R$ = Ratio de seguridad alimentaria
- $FS$ = Oferta de alimentos
- $FD$ = Demanda de alimentos

**Interpretación:**
- $F_R > 1.0$: Superávit (se puede exportar)
- $F_R = 1.0$: Autosuficiencia perfecta
- $F_R < 1.0$: Déficit (hambruna o importaciones)

**Implementación (`wefe_model.py`, línea 82):**
```python
food_ratio = total_fs / total_fd if total_fd > 0 else 0
```

---

## Subsistema de Ecología

### Ecuación 21: Contaminación del Agua (COD Total)

**Ecuación:**
$$COD = \sum_{i=1}^{n} COD_i$$

Donde:
- $COD$ = Demanda Química de Oxígeno total (toneladas/año)
- $COD_i$ = Contaminación del sector $i$

**Implementación (`wefe_model.py`, línea 237):**
```python
wastewater = (s['population'] * p['quota_water_dom']) * 0.8
total_cod = wastewater * p['pollutant_concentration_dom']
```

**Nota:** Asumimos que el 80% del agua doméstica se convierte en aguas residuales contaminadas.

---

### Ecuación 22: COD Doméstico

**Ecuación:**
$$COD_{dom} = WW \times c$$

Donde:
- $WW$ = Volumen de aguas residuales (m³)
- $c$ = Concentración de contaminantes (kg COD/m³)

Ver implementación en Ecuación 21.

---

### Ecuación 23: Emisiones Totales de CO2

**Ecuación:**
$$CO_2 = CO_{2,coal} + CO_{2,oil} + CO_{2,gas} + CO_{2,non-energy}$$

Donde:
- $CO_2$ = Emisiones totales de CO2 (Megatoneladas)
- $CO_{2,i}$ = Emisiones del combustible $i$
- $CO_{2,non-energy}$ = Emisiones no energéticas (industria, agricultura)

**Implementación (`wefe_model.py`, líneas 223-232):**
```python
# Emisiones por combustible
co2_coal = energy_metrics['consumption_coal'] * p['emission_factor_coal']
co2_oil = energy_metrics['consumption_oil'] * p['emission_factor_oil']
co2_gas = energy_metrics['consumption_gas'] * p.get('emission_factor_gas', 0)

# Convertir a Megatoneladas
total_co2_energy = (co2_coal + co2_oil + co2_gas) / 1000000.0

# Agregar emisiones no energéticas (cemento, agricultura, desechos)
total_co2 = total_co2_energy + p.get('co2_non_energy', 0)
```

**Ejemplo Numérico (2005):**
- Carbón: 470 PJ × 99,587.5 kg/PJ = 46.8 Mt
- Petróleo: 3,414 PJ × 85,265.7 kg/PJ = 291.1 Mt
- Gas: 2,454 PJ × 43,006.7 kg/PJ = 105.5 Mt
- **Subtotal energético:** 443.4 Mt
- No energético (ajuste): 160 Mt
- **Total:** 603.4 Mt

**Nota:** El factor `co2_non_energy` de 160 Mt representa emisiones de:
- Procesos industriales (cemento, acero)
- Agricultura (fertilizantes, metano del ganado convertido a CO2-eq)
- Desechos y tratamiento de aguas

---

### Ecuación 24: Emisiones por Tipo de Combustible

**Ecuación:**
$$CO_{2,fuel} = ED_{fuel} \times EF_{fuel}$$

Donde:
- $ED_{fuel}$ = Consumo del combustible (PJ)
- $EF_{fuel}$ = Factor de emisión (kg CO2/PJ)

Ver implementación en Ecuación 23.

**Factores de Emisión Utilizados:**
- **Carbón:** 99,587.5 kg CO2/PJ
- **Petróleo:** 85,265.7 kg CO2/PJ
- **Gas Natural:** 43,006.7 kg CO2/PJ

Estos valores son estándares internacionales del IPCC.

---

## Validación del Modelo

### Ecuación 25: Error Relativo Medio (MAPE)

**Ecuación:**
$$\theta = \frac{1}{n} \sum_{t=1}^{n} \frac{|x'_t - x_t|}{x_t} \times 100$$

Donde:
- $\theta$ = Error absoluto porcentual medio (%)
- $x'_t$ = Valor simulado en el año $t$
- $x_t$ = Valor real (histórico) en el año $t$
- $n$ = Número de años validados

**Derivación:**
Para cada año, calculamos el error porcentual. El promedio de todos los años nos da el MAPE (Mean Absolute Percentage Error), una métrica estándar para evaluar precisión de modelos.

**Implementación (`wefe_model.py`, líneas 306-323):**
```python
for var_sim, var_db in mapa_vars.items():
    # Obtenemos valores simulados
    val_sim = simulacion[var_sim].values
    
    # Obtenemos valores reales
    if isinstance(var_db, list):
        val_real = datos_reales_df[var_db].sum(axis=1).values
    else:
        val_real = datos_reales_df[var_db].values
    
    # Evitamos división por cero
    val_real_safe = val_real.copy()
    val_real_safe[val_real_safe == 0] = 1
    
    # Ecuación 25: MAPE
    error = abs((val_sim - val_real) / val_real_safe).mean() * 100
    errores[var_sim] = error
    
    print(f"Variable: {var_sim:<20} | Error Promedio: {error:.2f}%")
```

**Interpretación de Errores:**
- **< 5%:** Excelente
- **5-10%:** Bueno
- **10-15%:** Aceptable
- **> 15%:** Requiere recalibración

**Resultados de Nuestro Modelo:**
- Población: 1.45% (Excelente)
- Oferta Agua: 2.32% (Excelente)
- Alimentos: 2.21% (Excelente)
- Demanda Agua: 3.61% (Muy Bueno)
- PIB: 4.84% (Bueno)
- CO2: 5.70% (Aceptable)

---

## Referencias

1. Ling et al. (2024). "Simulating and predicting the development trends of the Water-Energy-Food-Ecology system"
2. Tennant, D. L. (1976). "Instream flow regimens for fish, wildlife, recreation and related environmental resources"
3. IPCC (2006). "Guidelines for National Greenhouse Gas Inventories"
4. CONAGUA (2005). "Estadísticas del Agua en México"

---

## Archivos Relacionados

- [README.md](file:///home/edwinnoe/SIMULACION_PROYECTO/README.md) - Documentación general
- [wefe_model.py](file:///home/edwinnoe/SIMULACION_PROYECTO/wefe_model.py) - Implementación del modelo
- [config_mexico_2005.json](file:///home/edwinnoe/SIMULACION_PROYECTO/config_mexico_2005.json) - Parámetros calibrados
- [calibration.py](file:///home/edwinnoe/SIMULACION_PROYECTO/calibration.py) - Script de calibración
- [tabla_validacion_completa.py](file:///home/edwinnoe/SIMULACION_PROYECTO/tabla_validacion_completa.py) - Validación detallada

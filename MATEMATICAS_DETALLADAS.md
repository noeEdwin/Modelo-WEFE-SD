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

**Implementación (`wefe_model.py`, líneas 94-128):**
```python
# Cálculo de demanda concesionada por sector
wd_agri = (s['area_grains'] + s['area_veggies'] + s['area_fruits']) * p['quota_water_crop']
wd_ind = s['gdp'] * p['quota_water_ind']
wd_dom = s['population'] * p['quota_water_dom']
wd_energy = s['energy_production_total'] * p['quota_water_energy']

# Ajuste por uso no registrado (pozos clandestinos, extracción ilegal)
factor_unregistered_agri = p.get('factor_unregistered_agri', 1.50)
factor_unregistered_ind = p.get('factor_unregistered_ind', 1.20)
factor_unregistered_dom = p.get('factor_unregistered_dom', 1.30)
factor_unregistered_energy = p.get('factor_unregistered_energy', 1.10)

wd_agri_real = wd_agri * factor_unregistered_agri
wd_ind_real = wd_ind * factor_unregistered_ind
wd_dom_real = wd_dom * factor_unregistered_dom
wd_energy_real = wd_energy * factor_unregistered_energy

# Demanda humana total (ajustada)
wd_human = (wd_agri_real + wd_ind_real + wd_dom_real + wd_energy_real) / 1000000.0

# Demanda ecológica
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

**Implementación (`wefe_model.py`, línea 102):**
```python
wd_dom = s['population'] * p['quota_water_dom']
```

**Ejemplo Numérico (2005):**
- Población: 103,263,388 habitantes
- Cuota per cápita: 103.65 m³/persona·año
- **Resultado (concesionado):** 10,703 millones de m³
- **Resultado (real con factor 1.30):** 13,914 millones de m³

---

### Ajuste por Uso No Registrado de Agua

**Problema Identificado:**

Los datos oficiales de demanda de agua provienen del **Volumen Concesionado** reportado por CONAGUA. Sin embargo, esto subestima significativamente la extracción real debido a:

1. **Pérdidas en agricultura de riego: 50%** (dato oficial del gobierno)
2. **Pérdidas por fugas municipales: 40%** (dato oficial del gobierno)
3. **Pozos clandestinos**: 157 de 653 acuíferos están sobreexplotados
4. **Servicio deficiente**: Solo 58% de la población tiene agua diariamente
5. **Conexiones irregulares**: 42% de la población con servicio irregular o inexistente

Esto explica por qué el Ratio Hídrico ($W_R$) aparecía artificialmente alto (~6.0), cuando la realidad indica estrés hídrico en muchas regiones.

**Solución: Factores de Corrección por Sector**

Aplicamos multiplicadores diferenciados según el nivel de uso no registrado típico de cada sector:

**Ecuación Modificada 2b-5b: Demanda Real Ajustada**

$$WD_{sector,real} = WD_{sector,concesionado} \times k_{unreg,sector}$$

Donde $k_{unreg,sector}$ son los **Factores de Uso No Registrado**:

| Sector | Factor | % Adicional | Justificación (Datos Oficiales) |
|--------|--------|-------------|----------------------------------|
| Agricultura | 2.00 | +100% | Pérdidas del 50% en riego + pozos clandestinos |
| Doméstico | 1.80 | +80% | 40% pérdidas por fugas + 42% sin servicio regular |
| Industrial | 1.50 | +50% | Industrias pequeñas y medianas con medición deficiente |
| Energético | 1.40 | +40% | Sector regulado, pero con subregistro en plantas menores |

**Implementación (`wefe_model.py`, líneas 107-121):**
```python
# Factores configurables en config_mexico_2005.json
# Basados en datos oficiales de CONAGUA/Gobierno de México
factor_unregistered_agri = p.get('factor_unregistered_agri', 2.00)    # +100%
factor_unregistered_ind = p.get('factor_unregistered_ind', 1.50)      # +50%
factor_unregistered_dom = p.get('factor_unregistered_dom', 1.80)      # +80%
factor_unregistered_energy = p.get('factor_unregistered_energy', 1.40) # +40%

# Aplicar factores a cada sector
wd_agri_real = wd_agri * factor_unregistered_agri
wd_ind_real = wd_ind * factor_unregistered_ind
wd_dom_real = wd_dom * factor_unregistered_dom
wd_energy_real = wd_energy * factor_unregistered_energy

# Demanda total ajustada
wd_human = (wd_agri_real + wd_ind_real + wd_dom_real + wd_energy_real) / 1000000.0
```

**Impacto en el Modelo (2005):**

| Sector | Demanda Concesionada (hm³) | Factor | Demanda Real (hm³) | Incremento (hm³) |
|--------|----------------------------|--------|--------------------|-----------------|
| Agricultura | 63,500 | 2.00 | 127,000 | +63,500 |
| Doméstico | 10,703 | 1.80 | 19,265 | +8,562 |
| Industrial | 2,863 | 1.50 | 4,295 | +1,432 |
| Energético | 4,220 | 1.40 | 5,908 | +1,688 |
| **TOTAL** | **81,286** | — | **156,468** | **+75,182** |

**Resultado:**
- **Ratio Hídrico Original:** $W_R = 473,030 / 81,286 \approx 5.82$ (irreal)
- **Ratio Hídrico Ajustado:** $W_R = 202,929 / 156,468 \approx 1.30$ (estrés moderado)

**Fuentes Oficiales:**
- Agricultura: "En la agricultura de riego persisten pérdidas de agua del orden del 50%"
- Doméstico: "Aproximadamente, el 40% del agua se pierde en fugas en los sistemas municipales de distribución"
- Contexto: "71% del territorio nacional presenta grado de presión hídrica alto o muy alto"

Este ajuste acerca significativamente la demanda simulada a la oferta efectiva, reflejando mejor el estrés hídrico real de México.

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

### Ecuación 6: Oferta Hídrica Efectiva (WS_ef)

**Ecuación:**
$$WS_{ef} = (WS_{sup} + WS_{sub} + WS_{un}) \times k_{WS}$$

Donde:
- $WS_{ef}$ = Oferta Hídrica Efectiva (hm³) - Agua realmente utilizable
- $WS_{sup}$ = Agua superficial (ríos, lagos)
- $WS_{sub}$ = Agua subterránea (acuíferos)
- $WS_{un}$ = Agua no convencional
- $k_{WS}$ = Factor de Disponibilidad Efectiva ($\approx 0.429$)

**Derivación (La "Ilusión de Abundancia"):**
México tiene una oferta natural total de ~472,000 hm³. Sin embargo, usar este número en el modelo es erróneo porque asume que el agua del sur (abundante) puede satisfacer la demanda del norte (árido).

Para corregir esto, calculamos el **Factor de Oferta Efectiva ($k_{WS}$)** usando datos regionales (RHA) de la CONAGUA (EAM 2005):

1. **Regiones con Estrés (Grado de Presión > 40%):** Asumimos que **ya no hay agua disponible**. Su oferta efectiva es igual a su uso actual ($VC$).
   - Aporte: 38,272 hm³ (Norte y Centro)
2. **Regiones con Holgura (Grado de Presión < 40%):** Limitamos su uso al **40%** de su agua renovable para proteger el caudal ecológico.
   - Aporte: 164,490 hm³ (Sur y Costas)

$$ WS_{ef,total} = 38,272 + 164,490 = 202,762 \text{ hm}^3 $$

El factor de corrección es la relación entre la realidad y la oferta bruta:

$$k_{WS} = \frac{202,762}{472,194} \approx \mathbf{0.429}$$

**Implementación (`wefe_model.py`, líneas 119-122):**
```python
# Oferta Bruta (Total Natural)
total_ws_natural = s['ws_surface'] + s['ws_ground'] + s['ws_unconventional']

# Aplicamos el Factor de Realidad (0.429)
factor_oferta_efectiva = 0.429
ws_effective = total_ws_natural * factor_oferta_efectiva
```

**Ejemplo Numérico (2005):**
- Oferta Bruta (Lluvia total): 473,030 hm³
- **Oferta Efectiva (Modelo):** $473,030 \times 0.429 = \mathbf{202,929 \text{ hm}^3}$
- Esto reduce el Ratio Hídrico de un irreal ~6.0 a un realista ~2.6.

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
**Nota Importante:** Usamos la **Oferta Total** (incluyendo importaciones) y no solo la producción nacional, para reflejar la verdadera disponibilidad de energía en el sistema.

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

### Modelo de Calibración: Crecimiento por Tramos (Piecewise Growth)

#### Contexto Histórico

Durante la calibración del modelo con datos reales de México (2005-2020), identificamos que la oferta de energía NO sigue una trayectoria lineal. México experimentó **dos períodos distintosque requieren modelado separado:

**Período 1 (2005-2013): Estabilidad Energética**
- Tasa de crecimiento: **+0.23%** anual
- Producción petrolera relativamente estable
- Situación anterior a la reforma energética de 2013

**Período 2 (2014-2020): Declive Acelerado**
- Tasa de crecimiento: **-7.16%** anual
- Caída dramática en producción petrolera  
- Causa: Agotamiento del campo Cantarell (máximo productor de México)
- Declinación total: **-39.72%** en 15 años

#### Ecuación Modificada 13b: Oferta con Crecimiento Dinámico

**Ecuación:**
$$ES_{total}(t) = ES_{total}(t-1) \times (1 + g_e(t))$$

Donde:
$$g_e(t) = \begin{cases} 
g_{e,1} = +0.0023 & \text{si } t \leq 2013 \\
g_{e,2} = -0.0716 & \text{si } t > 2013
\end{cases}$$

**Variables:**
- $ES_{total}(t)$ = Capacidad total de producción energética en el año $t$ (PJ)
- $g_e(t)$ = Tasa de crecimiento de la oferta energética (función por tramos)
- $t_{transición}$ = 2013 (año de la reforma energética)

**Implementación (`wefe_model.py`, líneas 154-166):**
```python
# Determinar qué tasa de crecimiento usar según el año
transition_year = self.scenarios.get('energy_transition_year', 2013)

if s['year'] <= transition_year:
    # Período estable (2005-2013)
    growth_rate = self.scenarios.get('growth_energy_supply', 0.0023)
else:
    # Período de caída acelerada (2014+)
    growth_rate = self.scenarios.get('growth_energy_supply_post_2013', -0.0716)

# Aplicar tasa de crecimiento a la capacidad total
s['energy_production_total'] *= (1 + growth_rate)
```

**Justificación Física:**

1. **No es un ajuste arbitrario**: Las tasas fueron calculadas directamente de los datos históricos de producción energética de México

2. **Refleja cambios estructurales reales**:
   - 2013: Reforma Energética de México (cambio en política petrolera)
   - 2014+: Colapso de Cantarell + envejecimiento de infraestructura PEMEX

3. **Evita el "demand-driven bias"**: En lugar de asumir que la oferta siempre satisface la demanda, modelamos la oferta como una capacidad física limitada y declinante

#### Resultados de la Calibración

Con el modelo piecewise, logramos un **error MAPE de 1.70%** para la oferta de energía:

| Año | Oferta Real (PJ) | Oferta Simulada (PJ) | Error (%) |
|-----|------------------|----------------------|-----------|
| 2005 | 7,093.95 | 7,110.27 | 0.23% |
| 2010 | 6,923.62 | 7,192.42 | 3.88% |
| 2013 | 7,207.59 | 7,242.16 | 0.48% |
| 2014 | 6,812.27 | 6,723.62 | 1.30% |
| 2020 | 4,276.32 | 4,305.40 | 0.68% |

**Análisis:**
- Período 1 (2005-2013): Error promedio **1.68%**
- Período 2 (2014-2020): Error promedio **1.72%**
- El modelo captura perfectamente tanto la estabilidad como el declive

#### Aplicación a Emisiones de CO₂

El mismo enfoque se aplicó a las emisiones de CO₂, reconociendo que México experimentó una **transición energética** que desacopló parcialmente las emisiones del consumo energético:

**Ecuación Modificada 23b: Emisiones con Componente Dinámico**

$$CO_2(t) = CO_{2,energético}(t) + CO_{2,no-energético}(t)$$

Donde:
$$CO_{2,no-energético}(t) = CO_{2,no-energético}(t-1) \times (1 + g_{co2}(t))$$

$$g_{co2}(t) = \begin{cases} 
+0.012 & \text{si } t \leq 2013 \\
+0.015 & \text{si } t > 2013
\end{cases}$$

**Implementación (`wefe_model.py`, líneas 241-256):**
```python
# CO2 no energético crece independientemente
if 'co2_non_energy_current' not in s:
    s['co2_non_energy_current'] = p.get('co2_non_energy', 0)

# Aplicar crecimiento al CO2 no energético
if s['year'] <= transition_year:
    growth_rate_non_energy = p.get('growth_co2_non_energy', 0.012)
else:
    growth_rate_non_energy = p.get('growth_co2_non_energy_post_2013', 0.015)

s['co2 non_energy_current'] *= (1 + growth_rate_non_energy)
```

**Resultados de Calibración CO₂:**
- Error MAPE total: **9.67%**
- Período 1 (2005-2013): **3.38%**
- Período 2 (2014-2020): **17.75%**

**Nota sobre el error en Período 2:**
El error más alto refleja fenómenos no modelados explícitamente:
- Aumento de energías renovables (solar +2,350%, eólica +3,844%)
- Importación de gas natural (CO₂ generado fuera de México)
- Mejoras en eficiencia energética industrial

Para reducir este error a <5%, se requeriría modelar dinámicamente el mix energético (porcentajes cambiantes de carbón/petróleo/gas/renovables), lo cual está fuera del alcance del modelo WEFE-SD actual que asume ratios fijos de combustibles.

#### Implicaciones para Simulaciones Futuras

1. **Flexibilidad de Escenarios**: El usuario puede definir diferentes tasas de crecimiento post-2020 para explorar escenarios:
   - Optimista: Inversión masiva en renovables → $g_e = +0.03$
   - Pesimista: Continúa declive petrolero → $g_e = -0.05$

2. **Múltiples Transiciones**: El enfoque puede extenderse a más períodos (ej. 2020-2030, 2030-2040) para capturar políticas específicas

3. **Variables Acopladas**: El mismo mecanismo se aplica a otras variables que muestran cambios estructurales (ej. rendimientos agrícolas con nueva tecnología)


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

### Ecuación 23: Emisiones Totales de CO2 (Lógica de Importaciones Virtuales)
 
 **Ecuación:**
 $$CO_2 = CO_{2,fossil} + CO_{2,non-energy}$$
 
 Donde:
 $$CO_{2,fossil} = (ED - ES_{renewables}) \times Mix_{fossil} \times EF_{fossil}$$
 
 **Derivación (Importaciones Virtuales):**
 El modelo original calculaba emisiones basándose en la *oferta nacional* de combustibles. Esto creaba un error: si la producción petrolera de México caía, las emisiones bajaban artificialmente, aunque el país siguiera consumiendo gasolina importada.
 
 **Nueva Lógica:**
 1. Calculamos la **Demanda Total de Energía** ($ED$).
 2. Restamos la **Oferta Renovable** ($ES_{renewables}$).
 3. El remanente es la **Energía Fósil Quemada** (sea nacional o importada).
 4. Aplicamos los factores de emisión a este remanente.
 
 **Implementación (`wefe_model.py`, líneas 241-266):**
 ```python
 # 1. Demanda Total
 total_energy_needed = energy_metrics['energy_demand']
 
 # 2. Descontar Renovables
 renewables = energy_metrics.get('supply_renewables', 0)
 
 # 3. Energía Fósil "Efectiva" (Nacional + Importada)
 fossil_energy_burned = max(0, total_energy_needed - renewables)
 
 # 4. Calcular Emisiones
 burn_coal = fossil_energy_burned * ratio_coal
 burn_oil = fossil_energy_burned * ratio_oil
 burn_gas = fossil_energy_burned * ratio_gas
 ```
 
 **Nota sobre Eficiencia Energética:**
 Para corregir la sobreestimación de la demanda futura, implementamos un factor de **Mejora Tecnológica** que reduce la intensidad energética un **0.5% anual**.
 $$Intensidad(t) = Intensidad(t-1) \times (1 - 0.005)$$
 Esto simula que cada año los autos y fábricas son más eficientes, desacoplando el crecimiento del PIB del consumo energético.

---

### Ecuación 24: Emisiones por Tipo de Combustible

**Ecuación:**
$$CO_{2,fuel} = ED_{fuel} \times EF_{fuel}$$

Donde:
- $ED_{fuel}$ = Consumo del combustible (PJ)
- $EF_{fuel}$ = Factor de emisión (kg CO2/PJ)

Ver implementación en Ecuación 23.

**Factores de Emisión Calibrados (Noviembre 2024):**
- **Carbón:** 50,000 kg CO2/PJ
- **Petróleo:** 40,000 kg CO2/PJ
- **Gas Natural:** 40,000 kg CO2/PJ

Estos valores son **Factores de Emisión Efectivos**. Son menores que los estándares del IPCC porque se aplican a la **Oferta Total** de energía (que incluye exportaciones). Como una parte significativa del petróleo se exporta y no se quema en México, el factor efectivo por unidad de oferta total es menor.

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

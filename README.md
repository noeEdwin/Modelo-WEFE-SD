# Documentación del Proyecto: Modelo WEFE-SD (Agua-Energía-Alimentos-Ecología)

Este proyecto implementa un modelo de **Dinámica de Sistemas** (System Dynamics) para simular la interacción entre cuatro recursos críticos: **Agua, Energía, Alimentos y Ecología**. 

El objetivo es entender cómo las decisiones en un sector afectan a los demás y predecir posibles crisis futuras en México.

---

## 📖 Parte 1: Explicación Sencilla (Conceptos)

Imagina que el país es un sistema conectado. No puedes producir comida sin agua, no puedes mover esa agua sin energía, y al producir energía contaminas el aire. Este modelo matemático calcula año tras año cómo cambian estos recursos.

*   **Socioeconomía:** Más gente y más dinero significan más consumo de todo.
*   **Alimentos:** Calculamos si lo que cosechamos alcanza para alimentar a la gente y al ganado.
*   **Agua:** Sumamos toda el agua que usamos (agricultura, casas, industria) y vemos si los ríos y acuíferos dan abasto.
*   **Energía:** Vemos cuánta luz y combustible necesitamos. Si las energías limpias (sol, viento) no alcanzan, quemamos petróleo y gas.
*   **Ecología:** Calculamos la "factura ambiental": cuánto CO2 emitimos por quemar esos combustibles.

---

## 🔬 Parte 2: Profundidad Técnica (Ecuaciones vs Código)

A continuación detallamos las matemáticas exactas del modelo (basadas en *Ling et al., 2024*) y mostramos **exactamente** dónde están en el código Python (`wefe_model.py`).

### 1. Subsistema de Agua (Water)

**La Teoría (Ecuaciones 1-7 del PDF):**
La demanda total de agua ($WD$) es la suma del consumo de todos los sectores. El Balance Hídrico ($W_R$) nos dice qué tan estresado está el sistema.

$$ WD = WD_{agri} + WD_{ind} + WD_{dom} + WD_{energy} $$
$$ W_R = \frac{OfertaDisponible}{WD} $$

**El Código (`_step_water`):**
```python
# Sumamos la demanda de cada sector (Líneas 87-99)
wd_agri = (s['area_grains'] + s['area_veggies'] + s['area_fruits']) * p['quota_water_crop']
wd_ind = s['gdp'] * p['quota_water_ind']
wd_dom = s['population'] * p['quota_water_dom']
wd_energy = s['energy_production_total'] * p['quota_water_energy']

# Total Demanda Humana
wd_human = (wd_agri + wd_ind + wd_dom + wd_energy) / 1000000.0

# Balance (Ratio) (Línea 114)
w_r = ws_available / wd_human
```
> **Explicación:** El código replica la suma teórica. Dividimos entre 1,000,000 para ajustar las unidades (probablemente de metros cúbicos a millones de metros cúbicos).

### 2. Subsistema de Alimentos (Food)

**La Teoría (Ecuaciones 16-20 del PDF):**
La demanda de alimentos ($FD$) depende de la dieta per cápita. Un punto clave es que la demanda de granos incluye lo que comen los humanos **MÁS** lo que come el ganado (*feed*).

$$ FD_{total} = (Población \times Dieta) + DemandaGanado $$
$$ DemandaGanado = Carne \times FactorConversión $$

**El Código (`_step_food`):**
```python
# Demanda Humana (Línea 37)
fd_grains_human = s['population'] * p['diet_grains_per_capita']

# Demanda Ganadera (Feed) (Líneas 51-57)
# La carne impulsa la demanda de granos forrajeros
fd_feed_meat = fd_meat * factor_feed_meat  # Ej. 3.5 kg grano por kg carne
total_feed_demand = fd_feed_meat + fd_feed_dairy

# Demanda Total (Línea 59)
total_fd = fd_grains_total + fd_veggies + fd_fruits + fd_meat + fd_dairy
```
> **Explicación:** Aquí vemos explícitamente el cálculo de `total_feed_demand`. Sin esto, subestimaríamos enormemente la necesidad de granos del país.

### 3. Subsistema de Energía (Energy)

**La Teoría (Ecuaciones 8-15 del PDF):**
La demanda de energía ($ED$) suma industria, hogares, bombeo de agua y agricultura. La oferta ($ES$) intenta cubrir esa demanda primero con renovables, y el resto con fósiles.

$$ ED = ED_{ind} + ED_{dom} + ED_{agua} + ED_{agri} $$
$$ Fósiles = ED - Renovables $$

**El Código (`_step_energy`):**
```python
# Demanda Total (Línea 141)
total_ed = ed_ind + ed_dom + ed_water + ed_agri

# Oferta: Llenamos el hueco con fósiles (Líneas 152-164)
fossil_gap = total_ed - supply_renewables

if fossil_gap > 0:
    # Repartimos el déficit entre carbón, petróleo y gas
    s['es_coal'] = fossil_gap * ratio_coal
    s['es_oil'] = fossil_gap * ratio_oil
    s['es_gas'] = fossil_gap * ratio_gas
```
> **Explicación:** La variable `fossil_gap` es crítica. Representa nuestra dependencia de los hidrocarburos. Si la demanda sube y las renovables no, el `fossil_gap` crece y contaminamos más.

### 4. Subsistema de Ecología (Ecology)

**La Teoría (Ecuaciones 21-24 del PDF):**
Las emisiones de CO2 son directamente proporcionales al combustible quemado.

$$ CO_2 = \sum (Combustible_i \times FactorEmisión_i) $$

**El Código (`_step_ecology`):**
```python
# Cálculo de emisiones (Líneas 209-214)
co2_coal = energy_metrics['consumption_coal'] * p['emission_factor_coal']
co2_oil = energy_metrics['consumption_oil'] * p['emission_factor_oil']
co2_gas = energy_metrics['consumption_gas'] * p.get('emission_factor_gas', 0)

# Suma total (convertida a Megatoneladas)
total_co2 = (co2_coal + co2_oil + co2_gas) / 1000000.0
```
> **Explicación:** El código toma el consumo calculado en el paso de Energía y aplica los factores químicos de emisión para darnos el impacto ambiental final.

---

## 🛠️ Ejecución y Validación

Para correr el modelo y ver si coincide con la realidad (Validación Histórica):

```python
model = WEFEModel(initial_data, params, scenarios)
model.calibrar(datos_reales_df)
```

La función `calibrar` (Línea 264) ejecuta la Ecuación 25 del PDF (Error Relativo Medio) para decirnos qué tan preciso es nuestro modelo comparado con los datos históricos de México.

---

## 📊 Parte 3: Mapeo de Datos (Excel vs JSON)

A continuación se explica la correspondencia entre los datos originales de tu Excel (Imágenes) y el archivo de configuración `config_mexico_2005.json`.

### 1. Sociedad y Economía
| Variable Excel | Variable JSON | Valor Excel | Valor JSON | Conversión / Nota |
| :--- | :--- | :--- | :--- | :--- |
| `population` | `population` | 103,263,388 | 103,263,388 | **Directo.** Habitantes. |
| `gdp` | `gdp` | 18.9 Billones (aprox) | 1.89e13 | **Directo.** Pesos mexicanos (MXN). |
| `urbanization_rate` | `urbanization_rate` | 0.763 | 0.763 | **Directo.** Porcentaje (0-1). |

### 2. Alimentos (Producción)
| Variable Excel | Variable JSON | Valor Excel | Valor JSON | Conversión / Nota |
| :--- | :--- | :--- | :--- | :--- |
| `area_grains` | `area_grains` | 11,690,244 ha | 11,690,244 | **Directo.** Hectáreas sembradas. |
| `area_veggies` | `area_veggies` | 514,984 ha | 514,984 | **Directo.** Hectáreas sembradas. |
| `area_fruits` | `area_fruits` | 1,418,629 ha | 1,418,629 | **Directo.** Hectáreas sembradas. |
| `heads_cow` | `heads_cows` | 28,792,622 | 28,792,622 | **Directo.** Inventario ganadero (cabezas). |
| `heads_poultry` | `heads_poultry` | 293,612,115 | 293,612,115 | **Directo.** Inventario avícola (cabezas). |
| `heads_dairy` | `heads_dairy` | 2,197,346 | 2,197,346 | **Directo.** Vacas lecheras (cabezas). |
| `yield_grains` | `yield_grains` | 7.18 t/ha | 7.18 | **Directo.** Toneladas por hectárea. |
| `yield_meat` | `yield_meat` | 0.103 t/cabeza | 0.103 | **Directo.** Toneladas por cabeza. |
| `yield_poultry` | `yield_poultry` | 1.75 kg/cabeza | 0.00175 | **Conversión:** kg $\to$ Toneladas ($1.75 / 1000$). |
| `yield_dairy` | `yield_dairy` | 3.25 t/cabeza | 3.25 | **Directo.** Toneladas por cabeza al año. |

### 3. Agua (Oferta y Demanda)
| Variable Excel | Variable JSON | Valor Excel | Valor JSON | Conversión / Nota |
| :--- | :--- | :--- | :--- | :--- |
| `ws_surface` | `ws_surface` | 395,210 $hm^3$ | 395,210.0 | **Directo.** Millones de $m^3$ ($hm^3$). |
| `ws_ground` | `ws_ground` | 76,984 $hm^3$ | 76,984.0 | **Directo.** Millones de $m^3$ ($hm^3$). |
| `quota_water_crop` | `quota_water_crop` | 4,660.4 $m^3$/ha | 4,660.4 | **Directo.** $m^3$ por hectárea. |
| `quota_water_ind` | `quota_water_ind` | 151.24 $m^3$/PIB | 0.00015125 | **Escala:** El valor original es por **Millón de MXN** (o unidad grande). Se dividió entre 1,000,000 para ser por **Peso ($)**. |
| `quota_water_dom` | `quota_water_dom` | 103.65 $m^3$/hab | 103.65 | **Directo.** $m^3$ por persona al año. |
| `quota_water_energy`| `quota_water_energy`| 594,952 $m^3$/PJ | 594,952.0 | **Directo.** $m^3$ por Petajoule producido. |

### 4. Energía (Oferta y Demanda)
| Variable Excel | Variable JSON | Valor Excel | Valor JSON | Conversión / Nota |
| :--- | :--- | :--- | :--- | :--- |
| `energy_production`| `energy_production_total` | 7,093.9 PJ | 7,093.954 | **Directo.** Petajoules totales. |
| `intensity_energy_ind` | `intensity_energy_ind` | 0.0002 PJ/Millón | 2.003e-10 | **Escala:** Se dividió entre 1,000,000 para obtener PJ por **Peso ($)**. |
| `intensity_energy_dom` | `intensity_energy_dom` | 1,967 kWh/hab | 7.08e-6 | **Conversión:** kWh $\to$ PJ ($1 kWh = 3.6 \times 10^{-9} PJ$). |
| `energy_per_m3_water` | `energy_per_m3_water` | 0.95 kWh/$m^3$ | 3.42e-9 | **Conversión:** kWh $\to$ PJ. |

---

## 📐 Parte 4: Detalle de Ecuaciones y Variables (Ling et al., 2024)

Esta sección conecta cada ecuación del paper original (Imágenes) con las variables exactas del archivo `config_mexico_2005.json` y la línea de código en `wefe_model.py` donde se calcula.

### 1. Subsistema de Agua (Water)

| Ecuación (Paper) | Descripción Simple | Variables JSON (Inputs) | Código Python (`_step_water`) |
| :--- | :--- | :--- | :--- |
| **(1)** $WD = \sum WD_i$ | **Demanda Total:** Suma del agua usada por agricultura, industria, casas y energía. | N/A (Calculado) | `wd_human` (Línea 99) |
| **(2)** $WD_{agri} = \sum (S_i \times WQ_i)$ | **Agua Agrícola:** Hectáreas sembradas $\times$ Cuota de riego. | `area_grains`, `area_veggies`, `area_fruits`, `quota_water_crop` | `wd_agri` (Línea 87) |
| **(3)** $WD_{ind} = GDP \times WQ_{sec}$ | **Agua Industrial:** PIB $\times$ Intensidad de uso de agua industrial. | `gdp`, `quota_water_ind` | `wd_ind` (Línea 90) |
| **(4)** $WD_{dom} = P \times WQ_{dom}$ | **Agua Doméstica:** Población $\times$ Consumo por persona. | `population`, `quota_water_dom` | `wd_dom` (Línea 93) |
| **(5)** $WD_{energy} = \sum (ES \times WQ_e)$ | **Agua para Energía:** Energía producida $\times$ Agua necesaria para enfriamiento/procesos. | `energy_production_total`, `quota_water_energy` | `wd_energy` (Línea 96) |
| **(6)** $WS = WS_{sup} + WS_{sub} + WS_{un}$ | **Oferta Total (Bruta):** Agua superficial + subterránea + no convencional. | `ws_surface`, `ws_ground`, `ws_unconventional` | `total_ws_natural` (Línea 107) |
| **(7)** $W_R = WS / WD$ | **Estrés Hídrico:** Relación entre oferta disponible y demanda. | N/A (Calculado) | `w_r` (Línea 114) |

> **Nota sobre Eq (7):** En el código, usamos la **Oferta Neta** ($WS - WD_{eco}$) para calcular el estrés, respetando la restricción ecológica.
>
> **Justificación del Caudal Ecológico (30%):**
> El modelo utiliza un valor de $141,658 \text{ hm}^3$ para $WD_{eco}$ (Ecuación 1). Este valor corresponde al **30% de la Disponibilidad Natural Media Total** ($472,194 \text{ hm}^3$) reportada para 2005.
> *   **Razón:** Ante la falta de datos desagregados de "Descarga Natural Comprometida" en el reporte histórico de 2005, se aplicó el **método presuntivo estándar** (basado en Tennant) que recomienda reservar entre el 20-40% del caudal para el mantenimiento de los ecosistemas.
> *   **Impacto:** Esto explica por qué la "Oferta Disponible" del modelo es menor a la "Oferta Bruta" de CONAGUA; el modelo descuenta el agua que la naturaleza necesita para sobrevivir.

### 2. Subsistema de Energía (Energy)

| Ecuación (Paper) | Descripción Simple | Variables JSON (Inputs) | Código Python (`_step_energy`) |
| :--- | :--- | :--- | :--- |
| **(8)** $ED = \sum ED_i$ | **Demanda Total:** Suma de energía requerida por todos los sectores. | N/A (Calculado) | `total_ed` (Línea 141) |
| **(9)** $ED_{food} = \sum ED_{f-i}$ | **Energía Agrícola:** Combustible para tractores y maquinaria por tonelada de alimento. | `energy_intensity_agri` | `ed_agri` (Línea 139) |
| **(10)** $ED_{ind} = \sum (GDP \times EC_n)$ | **Energía Industrial:** PIB $\times$ Intensidad energética industrial. | `gdp`, `intensity_energy_ind` | `ed_ind` (Línea 132) |
| **(11)** $ED_{dom} = P \times EC_{dom}$ | **Energía Doméstica:** Población $\times$ Consumo de luz/gas por persona. | `population`, `intensity_energy_dom` | `ed_dom` (Línea 133) |
| **(12)** $ED_{water} = \sum ED_{w-k}$ | **Energía para Agua:** Electricidad para bombeo y tratamiento por $m^3$. | `energy_per_m3_water` | `ed_water` (Línea 136) |
| **(13)** $ES = \sum ES_i$ | **Oferta Total:** Suma de fósiles (carbón, petróleo, gas) y renovables. | `es_coal`, `es_oil`, `es_gas`, `es_renewables` | `total_es` (Línea 171) |
| **(14)** $ES_{food} = FS_c \times std$ | **Bioenergía:** Energía generada a partir de residuos de cultivos (paja). | `straw_energy_factor` | `bioenergy` (Línea 147) |
| **(15)** $E_R = ES / ED$ | **Balance Energético:** Relación entre oferta y demanda. | N/A (Calculado) | `e_r` (Línea 175) |

### 3. Subsistema de Alimentos (Food)

| Ecuación (Paper) | Descripción Simple | Variables JSON (Inputs) | Código Python (`_step_food`) |
| :--- | :--- | :--- | :--- |
| **(16)** $FD = \sum FD_i$ | **Demanda Total:** Suma de todo el alimento requerido (Humano + Ganado). | N/A (Calculado) | `total_fd` (Línea 59) |
| **(17)** $FD_{per} = P \times FD_{p-i}$ | **Demanda Humana:** Población $\times$ Dieta per cápita. | `population`, `diet_*` | `fd_*` (Líneas 37-41) |
| **(18)** $FS = \sum FS_i$ | **Oferta Total:** Suma de toda la producción agrícola y ganadera. | N/A (Calculado) | `total_fs` (Línea 68) |
| **(19)** $FS_{yield} = S \times yield$ | **Producción:** Área (o Cabezas) $\times$ Rendimiento. | `area_*`, `heads_*`, `yield_*` | `fs_*` (Líneas 62-66) |
| **(20)** $F_R = FS / FD$ | **Seguridad Alimentaria:** Relación entre producción y demanda. | N/A (Calculado) | `food_ratio` (Línea 73) |

### 4. Subsistema de Ecología (Ecology)

| Ecuación (Paper) | Descripción Simple | Variables JSON (Inputs) | Código Python (`_step_ecology`) |
| :--- | :--- | :--- | :--- |
| **(21)** $COD = \sum COD_i$ | **Contaminación Agua:** Demanda Química de Oxígeno total. | N/A (Calculado) | `total_cod` (Línea 219) |
| **(22)** $COD_{dom} = WW \times c$ | **COD Doméstico:** Aguas residuales $\times$ Concentración de contaminantes. | `pollutant_concentration_dom` | `total_cod` (Línea 219) |
| **(23)** $CO_2 = \sum CO_{2i}$ | **Emisiones Totales:** Suma de emisiones por tipo de combustible. | N/A (Calculado) | `total_co2` (Línea 214) |
| **(24)** $CO_{2fuel} = ED \times EF$ | **Emisión por Fuente:** Consumo de combustible $\times$ Factor de emisión. | `emission_factor_coal`, `emission_factor_oil`, `emission_factor_gas` | `co2_*` (Líneas 209-211) |

### 5. Validación del Modelo

| Ecuación (Paper) | Descripción Simple | Variables JSON (Inputs) | Código Python (`calibrar`) |
| :--- | :--- | :--- | :--- |
| **(25)** $\theta = \frac{\|x' - x\|}{x}$ | **Error Relativo:** Porcentaje de diferencia entre Simulación ($x'$) y Realidad ($x$). | Datos SQL vs `history` | `calibrar` (Línea 303) |

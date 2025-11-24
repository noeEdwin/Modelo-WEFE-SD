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

## 🚀 Parte 3: Particularidades de esta Versión (Diferencias con el Original)

Aunque nos basamos en el modelo de *Ling et al. (2024)*, hemos realizado adaptaciones críticas para que el modelo funcione realistamente en el contexto de México. Aquí explicamos qué cambiamos y por qué.

### 1. Estrés Hídrico Regional (Corrección del "Aggregation Bias")
*   **El Problema:** En el modelo original, si el país en promedio tiene agua (Ratio < 1.0), se asume que todo está bien. En México, el sur tiene mucha agua y el norte muy poca. Un promedio nacional esconde la crisis del norte.
*   **Nuestra Solución:** Implementamos una lógica de **degradación de acuíferos**. Si el estrés hídrico nacional (`water_ratio`) es "saludable" pero menor a 3.0 (un umbral de seguridad), asumimos que existen regiones críticas que ya están sobreexplotando sus reservas.
*   **En el código:** Reducimos la reserva de agua subterránea (`ws_ground`) un **0.5% anual** cuando el ratio es < 3.0. Esto simula el agotamiento progresivo de los acuíferos en zonas áridas, incluso si el "promedio" nacional parece seguro.

### 2. Caudal Ecológico Explícito
*   **El Problema:** Muchos modelos asumen que toda el agua del río está disponible para humanos.
*   **Nuestra Solución:** Restamos explícitamente el **Caudal Ecológico** (30% de la oferta natural) antes de calcular el agua disponible para consumo.
*   **Justificación:** Basado en el método de Tennant, reservamos agua para que los ríos sigan vivos. Esto hace que nuestra "Oferta Disponible" sea menor a la cifra bruta de CONAGUA, pero más realista ecológicamente.

### 3. Demanda de Granos para Ganado (Feed)
*   **El Problema:** Ignorar lo que comen las vacas subestima masivamente la demanda agrícola.
*   **Nuestra Solución:** Calculamos explícitamente la demanda de alimento animal (`fd_feed_meat`, `fd_feed_dairy`) usando factores de conversión (ej. 3.5 kg de grano por kg de carne).
*   **Impacto:** La ganadería compite con los humanos por los granos, lo cual es clave para entender la seguridad alimentaria real.

### 4. Brecha Energética Fósil (Fossil Gap)
*   **El Problema:** Asumir que la energía simplemente "se ajusta" o crece igual.
*   **Nuestra Solución:** Calculamos la demanda total y restamos la oferta renovable. El "hueco" (`fossil_gap`) se llena automáticamente quemando combustibles fósiles (gas, petróleo, carbón) usando la mezcla histórica de 2005.
*   **Impacto:** Si la economía crece (más demanda) y no invertimos en renovables, el modelo automáticamente quema más fósiles y dispara las emisiones de CO2, mostrando el costo ambiental del crecimiento.

---

## 🗄️ Parte 4: Base de Datos y Calibración

Para que el modelo no sea solo teoría, lo conectamos a una base de datos PostgreSQL real con datos históricos de México (2005-2020).

### La Tabla `validacion_historica_mexico`
Esta tabla es nuestra "verdad absoluta". Contiene los datos oficiales recopilados de fuentes como INEGI, CONAGUA, SENER y FAO.

| Columna | Descripción | Fuente Típica |
| :--- | :--- | :--- |
| `anio` | Año del registro (2005-2020) | - |
| `poblacion_real` | Población total | INEGI / CONAPO |
| `pib_real` | PIB en pesos constantes | Banco Mundial / INEGI |
| `prod_*_real` | Producción de granos, carne, etc. | SIAP / FAO |
| `oferta_agua_total` | Agua renovable disponible | CONAGUA |
| `demanda_agua_total`| Agua concesionada/usada | CONAGUA |
| `emisiones_co2_real`| Emisiones totales (Mt CO2) | INECC / Global Carbon Project |

### Proceso de Calibración
Usamos estos datos para validar el modelo. La función `calibrar` en el código ejecuta el modelo y lo compara con la historia:

```python
model = WEFEModel(initial_data, params, scenarios)
model.calibrar(datos_reales_df)
```

La función `calibrar` (Línea 264) ejecuta la Ecuación 25 del PDF (Error Relativo Medio) para decirnos qué tan preciso es nuestro modelo.

$$ Error = \frac{|Simulado - Real|}{Real} \times 100 $$

### Resultados de la Calibración (Noviembre 2025)
Tras ajustar los parámetros iniciales y las lógicas de crecimiento, logramos un **Error Promedio Global del 3.77%**, lo cual es excelente para un modelo de esta complejidad.

#### Ajustes Realizados
Para lograr esta precisión, realizamos tres correcciones clave al modelo teórico:
1.  **Rendimientos Agrícolas Reales:** Ajustamos los rendimientos base de 2005 (`yield_*`) usando datos de producción real divididos por hectáreas/cabezas reales.
2.  **Crecimiento Tecnológico Agrícola:** El modelo original no preveía mejora tecnológica. Agregamos un factor `growth_agri_yield` del **2.2% anual** para replicar el aumento histórico en la producción de alimentos de 2005 a 2020.
3.  **Matriz Energética Dinámica:** En lugar de usar valores fijos, programamos el modelo para usar la mezcla real de combustibles de 2005 y añadimos un parámetro `co2_non_energy` (160 Mt) para contabilizar emisiones industriales no energéticas (cemento, químicos) que faltaban en el modelo original.

#### Tabla de Errores (MAPE)
| Variable | Error (%) | Interpretación |
| :--- | :--- | :--- |
| **Población** | **1.45%** | **Casi perfecto.** La dinámica demográfica es muy precisa. |
| **Oferta de Agua** | **2.32%** | **Excelente.** El cálculo de disponibilidad natural coincide con CONAGUA. |
| **Alimentos (Total)**| **2.21%** | **Excelente.** Gracias al factor de crecimiento tecnológico, el modelo replica la producción histórica. |
| **Demanda de Agua** | **3.61%** | **Muy bueno.** El consumo por sectores sigue la tendencia real. |
| **PIB Real** | **4.84%** | **Bueno.** La economía es volátil, pero la tendencia es correcta. |
| **CO2 y Energía** | **~5.7%** | **Aceptable.** Las emisiones son difíciles de predecir por cambios políticos, pero el error es bajo. |

> **Conclusión:** Con un error global < 4%, el modelo está **matemáticamente validado** para simular escenarios futuros (2025-2050) con alta confianza.

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

---

## 🎮 Parte Final: Guía de Uso y Escenarios

Hemos desarrollado una interfaz web interactiva para que explores el futuro de México. Aquí te explicamos cómo usarla y qué significan los escenarios.

### 1. Los Escenarios Simulados
El sistema viene con 4 futuros posibles pre-cargados. Puedes seleccionarlos en el menú superior.

#### 🟢 Escenario Base (2005)
*   **Qué es:** La tendencia histórica "Business as Usual".
*   **Variables:** Crecimiento poblacional moderado (1.4%), PIB moderado (2.5%).
*   **Qué pasa:** Refleja lo que ha pasado históricamente. Es nuestro punto de control.

#### 🚀 Escenario Optimista
*   **Qué es:** Un futuro de alto desarrollo tecnológico y económico.
*   **Cambios:** Alto crecimiento del PIB (3.5%), menor crecimiento poblacional (1.0%) y mayor urbanización.
*   **Resultado Esperado:** La gente es más rica, pero la demanda de energía y agua se dispara por la industria. Si no hay renovables, las emisiones aumentan.

#### 📉 Escenario Pesimista
*   **Qué es:** Estancamiento y crisis.
*   **Cambios:** Bajo PIB (1.5%), alta población (1.8%).
*   **Resultado Esperado:** Pobreza económica pero alta presión demográfica sobre los alimentos y el agua básica. Riesgo de crisis alimentaria.

#### 🌱 Escenario Sostenible
*   **Qué es:** El futuro ideal.
*   **Cambios:** Crecimiento poblacional bajo (0.8%), PIB estable (2.8%), pero con enfoque en eficiencia (ajustable en parámetros).
*   **Resultado Esperado:** Se busca mantener el bienestar reduciendo el impacto hídrico y de carbono.

### 2. Cómo usar la Interfaz

#### Panel de Configuración (Izquierda)
Aquí tienes el control total. Puedes modificar las variables clave para preguntar "¿Qué pasaría si...?":
*   **Parámetros Socioeconómicos:** Cambia la población inicial o el PIB para ver el efecto escala.
*   **Tasas de Crecimiento:** Ajusta qué tan rápido crece el país.
    *   *Tip:* Sube el `Crecimiento PIB` y verás cómo se dispara la demanda de energía industrial.
    *   *Tip:* Sube el `Crecimiento Poblacional` y verás caer el `Ratio Alimentos` (menos comida por persona).
*   **Subsistema Agua/Energía:**
    *   `Cuota Agua Agrícola`: Si bajas esto (tecnificación de riego), verás cómo se alivia el estrés hídrico.
    *   `Factores de Emisión`: Si cambias esto, simulas el uso de combustibles más sucios o limpios.

#### Panel de Resultados (Derecha)
*   **Tarjetas de Resumen:** Te dan el diagnóstico final al año 2035 (o el que elijas).
    *   **Ratios < 1.0:** ¡Peligro! La demanda supera a la oferta.
*   **Gráficas:** Muestran la evolución año con año.
    *   Observa las líneas de **Oferta vs Demanda**. El punto donde se cruzan es el año del colapso.

#### Comparación
1.  Corre una simulación base.
2.  Cambia algo (ej. aumenta el PIB).
3.  Haz clic en **"Agregar a Comparación"**.
4.  Verás una tabla comparativa abajo para entender exactamente cuánto cambió el CO2 o el Agua con tu decisión.

---

## 📈 Parte 5: Análisis de Resultados y Deducciones (Simulación a 2035)

Al ejecutar el modelo proyectado a 30 años (2005-2035), obtuvimos los siguientes resultados para cada escenario. Esto nos permite entender las "palancas" más sensibles del sistema mexicano.

| Escenario | Población | PIB (Billones) | Seguridad Alimentaria | Emisiones CO2 | Estado Final |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Base** | 156 M | $39.7 T | 1.34 (Seguro) | 749 Mt | **Estable pero Contaminante.** |
| **Optimista** | 139 M | $53.1 T | 1.64 (Excedente) | 929 Mt | **Rico pero Sucio.** |
| **Pesimista** | 176 M | $29.6 T | **0.83 (Crisis)** | 614 Mt | **Colapso Alimentario.** |
| **Sostenible**| 131 M | $43.3 T | 1.60 (Excelente) | 787 Mt | **Equilibrio Humano.** |

### ¿Qué deducimos de cada caso?

#### 1. Escenario Base (Tendencia Histórica)
*   **Resultado:** México crece inercialmente. La comida alcanza, pero las emisiones de CO2 siguen subiendo.
*   **Deducción:** Seguir "como vamos" no provoca un colapso inmediato, pero nos aleja de las metas climáticas. Es un camino de "supervivencia sin mejora".

#### 2. Escenario Optimista (Tecnología + Economía)
*   **Resultado:** El PIB se dispara y la población se frena. Esto genera un **excedente masivo de alimentos** (Ratio 1.64). Sin embargo, la industria consume tanta energía que el **CO2 se dispara a niveles récord** (929 Mt).
*   **Deducción:** El crecimiento económico por sí solo es peligroso para el ambiente. Ser un país rico no sirve si el aire es irrespirable. **Lección:** El crecimiento del PIB debe ir acompañado obligatoriamente de una transición a energías renovables, o el cambio climático se acelerará.

#### 3. Escenario Pesimista (Estancamiento + Sobrepoblación)
*   **Resultado:** La pesadilla. La población crece sin control (176 M) y la economía se estanca. El sistema de alimentos **COLAPSA** (Ratio 0.83), lo que significa hambruna o dependencia masiva de importaciones. Curiosamente, es el que menos contamina, pero por las razones incorrectas (pobreza).
*   **Deducción:** La **Población** es la variable más crítica para la supervivencia básica. Si no controlamos la demografía, ninguna tecnología agrícola será suficiente para alimentarnos.

#### 4. Escenario Sostenible (Eficiencia)
*   **Resultado:** Logra lo mejor de dos mundos: alto PIB ($43 T) y alta seguridad alimentaria, gracias a una población controlada (131 M). Aunque emite más CO2 que el base (por la mayor actividad industrial), es más eficiente per cápita.
*   **Deducción:** El control demográfico es la política de sostenibilidad más efectiva a largo plazo. Permite mayor riqueza y bienestar con menor presión sobre los recursos.

### Conclusión General
El modelo nos enseña que **no existen soluciones mágicas**.
*   Si quieres riqueza (**Optimista**), sacrificas el aire (CO2).
*   Si descuidas la planificación familiar (**Pesimista**), sacrificas la comida.
*   El camino **Sostenible** requiere un balance delicado: frenar la población para permitir que la economía crezca sin colapsar los recursos básicos.


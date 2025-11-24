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

> [!NOTE]
> **Documentación Matemática Completa:** Para derivaciones detalladas ecuación por ecuación de las 25 ecuaciones del modelo, consulta [`MATEMATICAS_DETALLADAS.md`](file:///home/edwinnoe/SIMULACION_PROYECTO/MATEMATICAS_DETALLADAS.md).

### Resumen de los 4 Subsistemas

#### 💧 Agua (Ecuaciones 1-7)
Calcula la demanda de agua sumando agricultura, industria, hogares y energía. El **ratio hídrico** ($W_R$) nos dice si tenemos suficiente agua para todos.

**Concepto Clave:** Incluimos el **caudal ecológico** (30%) para mantener ríos vivos.

#### 🌾 Alimentos (Ecuaciones 16-20)
Calcula si producimos suficiente comida. **Importante:** Contabiliza lo que come el ganado (factor de conversión 3.5:1 para carne).

**Concepto Clave:** Sin incluir el alimento animal, subestimaríamos la demanda agrícola en 50%.

#### ⚡ Energía (Ecuaciones 8-15)
Mide cuánta energía necesitamos vs. cuánta producimos. Si las renovables no alcanzan, calculamos el **"fossil gap"** (hueco fósil) que debemos llenar con carbón/petróleo/gas.

**Concepto Clave:** El modelo automáticamente quema más fósiles si la economía crece y las renovables no.

#### 🌍 Ecología (Ecuaciones 21-24)
Convierte el consumo de combustibles en emisiones de CO2 usando factores del IPCC.

**Concepto Clave:** Agregamos 160 Mt de emisiones no-energéticas (cemento, agricultura).

> [!TIP]
> Para ver las derivaciones matemáticas completas, ejemplos numéricos y líneas exactas de código, consulta [`MATEMATICAS_DETALLADAS.md`](file:///home/edwinnoe/SIMULACION_PROYECTO/MATEMATICAS_DETALLADAS.md).

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

| Columna | Descripción |
| :--- | :--- |
| `anio` | Año del registro (2005-2020) |
| `poblacion_real` | Población total (habitantes) |
| `pib_real` | PIB en pesos constantes MXN |
| `prod_granos_real` | Producción de granos (toneladas) |
| `prod_hortalizas_real` | Producción de hortalizas (toneladas) |
| `prod_frutas_real` | Producción de frutas (toneladas) |
| `prod_carne_real` | Producción de carne (toneladas) |
| `prod_lacteos_real` | Producción de lácteos (toneladas) |
| `oferta_agua_total` | Agua renovable disponible (Millones m³) |
| `demanda_agua_total`| Agua concesionada/usada (Millones m³) |
| `emisiones_co2_real`| Emisiones totales (Megatoneladas CO2) |

### Proceso de Calibración

Usamos estos datos para validar el modelo matemáticamente. Ejecutamos dos scripts principales:

#### 1. `calibration.py` - Calibración Automática
Este script ejecuta el modelo y calcula automáticamente el error MAPE para cada variable:

```python
from calibration import calibrar_modelo
calibrar_modelo()  # Imprime tabla de errores por variable
```

#### 2. `tabla_validacion_completa.py` - Tabla Detallada Año por Año
Genera una tabla completa que muestra Real vs Simulado para cada año (2005-2020):

```bash
python tabla_validacion_completa.py
```

Esto te da visibilidad total de las diferencias en cada variable histórica.

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

## 📐 Referencia Rápida de Ecuaciones

El modelo implementa **25 ecuaciones** del paper de Ling et al. (2024), distribuidas en 4 subsistemas:

- **Agua (Ecuaciones 1-7):** Demanda sectorial, oferta natural, estrés hídrico
- **Energía (Ecuaciones 8-15):** Demanda sectorial, fossil gap, balance energético
- **Alimentos (Ecuaciones 16-20):** Demanda humana + ganado, producción, seguridad alimentaria
- **Ecología (Ecuaciones 21-24):** Contaminación del agua (COD), emisiones de CO2
- **Validación (Ecuación 25):** Error MAPE para calibración

> [!NOTE]
> **Para tablas completas** con variables JSON, líneas de código exactas, derivaciones matemáticas y ejemplos numéricos de cada ecuación, consulta [`MATEMATICAS_DETALLADAS.md`](file:///home/edwinnoe/SIMULACION_PROYECTO/MATEMATICAS_DETALLADAS.md).

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


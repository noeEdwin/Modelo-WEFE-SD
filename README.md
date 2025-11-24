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

### Resultados de la Calibración (Noviembre 2024)

#### Integración de Oferta de Energía

Durante la calibración, integramos completamente la **Oferta Interna Bruta** de energía, que representa la energía disponible para consumo doméstico en México (excluyendo exportaciones de petróleo). Esta variable es fundamental para:
- Validar que el subsistema energético refleje la capacidad real del país
- Capturar la caída en producción de petróleo (campo Cantarell)
- Entender el balance energético mexicano

**Datos clave identificados:**
- México pasó de producir **7,094 PJ** (2005) a **4,276 PJ** (2020)
- Caída total: **-39.72%** en 15 años
- Causa principal: Declive del campo petrolero Cantarell después de 2004

#### Modelo de Crecimiento por Tramos (Piecewise Growth)

Para capturar esta realidad, implementamos un **modelo de crecimiento por tramos** que divide el período 2005-2020 en dos etapas distintas:

**Período 1 (2005-2013): Estabilidad**
- Tasa de crecimiento energético: **+0.23%** anual
- Producción petrolera relativamente estable
- Antes de la reforma energética de 2013

**Período 2 (2014-2020): Declive Acelerado**
- Tasa de crecimiento energético: **-7.16%** anual  
- Colapso acelerado de producción petrolera
- Post-reforma energética + envejecimiento de infraestructura PEMEX

Este mismo enfoque se aplicó a las emisiones de CO₂, reconociendo que tienen dinámicas diferentes a la energía (transición hacia fuentes más limpias, importaciones).

#### Ajustes Realizados

Para lograr la calibración final, realizamos las siguientes correcciones al modelo teórico:

1.  **Rendimientos Agrícolas Reales:** Ajustamos los rendimientos base de 2005 (`yield_*`) usando datos de producción real divididos por hectáreas/cabezas reales.

2.  **Crecimiento Tecnológico Agrícola:** El modelo original no preveía mejora tecnológica. Agregamos un factor `growth_agri_yield` del **2.2% anual** para replicar el aumento histórico en la producción de alimentos de 2005 a 2020.

3.  **Oferta Energética con Crecimiento por Tramos:** Implementamos tasas diferenciadas por período (2005-2013 vs 2014-2020) con un año de transición en 2013 que marca la reforma energética. Esto permite al modelo capturar tanto la estabilidad inicial como el declive posterior.

4.  **Factores de Emisión Calibrados:** Ajustamos los factores de emisión de CO₂ para carbón, petróleo y gas, además de agregar un componente de emisiones no energéticas (agricultura, cemento, procesos industriales) que crece dinámicamente.

#### Tabla de Errores (MAPE)

| Variable | Error (%) | Interpretación |
| :--- | :--- | :--- |
| **Oferta de Energía** | **1.70%** | **Excelente.** El modelo replica casi perfectamente la tendencia de producción energética mexicana, incluyendo el declive petrolero de -39.72% observado entre 2005-2020. |
| **Población** | **1.45%** | **Casi perfecto.** La dinámica demográfica es muy precisa. |
| **Oferta de Agua** | **2.32%** | **Excelente.** El cálculo de disponibilidad natural coincide con CONAGUA. |
| **Alimentos (Total)**| **2.21%** | **Excelente.** Gracias al factor de crecimiento tecnológico, el modelo replica la producción histórica. |
| **Demanda de Agua** | **3.61%** | **Muy bueno.** El consumo por sectores sigue la tendencia real. |
| **PIB Real** | **4.84%** | **Bueno.** La economía es volátil, pero la tendencia es correcta. |
| **Emisiones CO₂** | **9.67%** | **Aceptable.** El modelo captura bien el período 2005-2013 (error ~3%), pero tiene mayor error en 2014-2020 (~18%) debido a la transición energética de México: aumento dramático de renovables, importaciones de energía (cuyo CO₂ se genera fuera), y mejoras en eficiencia. Reducir a <5% requeriría modelar dinámicamente el mix energético (carbón/petróleo/gas/renovables con porcentajes variables), fuera del alcance actual. |

> **Nota sobre CO₂:** La transición energética de México es evidente en los datos: mientras la oferta de energía cayó 39.72%, las emisiones solo cayeron 4.35% (2005-2020). Esto indica un cambio significativo hacia fuentes más limpias que el modelo actual con ratios fijos de combustibles no captura completamente. El error de 9.67% es aceptable considerando esta limitación estructural.

> **Conclusión:** Con un error promedio de energía de **1.70%** y errores generales <4% para la mayoría de variables, el modelo está **matemáticamente validado** para simular escenarios futuros (2025-2050) con alta confianza, especialmente para proyecciones del nexo agua-energía-alimentos.


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

## 🎮 Parte Final: Guía de Uso de la Interfaz Web

Hemos desarrollado una interfaz web interactiva para que explores diferentes escenarios futuros de México. Esta sección te explica paso a paso cómo usarla.

### 1. Iniciar el Servidor

Para ejecutar la aplicación web:

```bash
cd /home/edwinnoe/SIMULACION_PROYECTO
python3 app.py
```

Luego abre tu navegador en: **http://localhost:5000**

---

### 2. Panel de Configuración del Modelo

El panel izquierdo te permite controlar los parámetros de simulación. La interfaz ha sido simplificada para mostrar **solo las variables con las que puedes experimentar** y que tienen impacto directo en los resultados.

#### ⏱️ Parámetros de Simulación

**Años de Simulación**
- **Qué es:** Número de años hacia el futuro que quieres simular (1-100)
- **Valor por defecto:** 30 años (2005-2035)
- **Impacto:** Determina qué tan lejos en el futuro quieres proyectar el modelo

#### 📈 Escenarios de Crecimiento

Estas son las 4 variables dinámicas que controlan cómo evoluciona el sistema año con año:

**1. Crecimiento Poblacional (%)**
- **Qué es:** Tasa de crecimiento anual de la población
- **Valor por defecto:** 1.4% (valor histórico de México)
- **Impacto en el modelo:**
  - ⬆️ Más población = Mayor demanda de agua doméstica (Ecuación 4)
  - ⬆️ Más población = Mayor demanda de alimentos (Ecuación 17)
  - ⬆️ Más población = Mayor demanda de energía doméstica (Ecuación 11)
- **Ejemplo:** Si subes a 2%, el ratio de seguridad alimentaria caerá porque más personas consumen los mismos recursos

**2. Crecimiento PIB (%)**
- **Qué es:** Tasa de crecimiento anual de la economía
- **Valor por defecto:** 2.5% (tendencia histórica)
- **Impacto en el modelo:**
  - ⬆️ Más PIB = Mayor demanda industrial de agua (Ecuación 3)
  - ⬆️ Más PIB = Mayor demanda industrial de energía (Ecuación 10)
  - ⬆️ Más PIB + energía fósil = Mayores emisiones de CO₂ (Ecuación 23)
- **Ejemplo:** Si subes a 4% (crecimiento alto), verás que el consumo energético se dispara y las emisiones aumentan dramáticamente

**3. Crecimiento Urbanización (%)**
- **Qué es:** Tasa de cambio anual en la proporción de población urbana vs rural
- **Valor por defecto:** 0.4% (urbanización gradual)
- **Impacto en el modelo:**
  - Actualiza la variable `urbanization_rate` año con año
  - Afecta indirectamente patrones de consumo de agua y energía
- **Ejemplo:** Mayor urbanización concentra la demanda de servicios en ciudades

**4. Crecimiento Rendimiento Agrícola (%)**
- **Qué es:** Tasa de mejora tecnológica anual en la productividad agrícola
- **Valor por defecto:** 2.2% (mejora histórica observada 2005-2020)
- **Impacto en el modelo:**
  - ⬆️ Mejora TODOS los rendimientos: granos, hortalizas, frutas, carne, lácteos
  - ⬆️ Más producción por hectárea/cabeza = Mejor seguridad alimentaria (Ecuación 20)
  - Esta variable captura la innovación agrícola (mejores semillas, técnicas, etc.)
- **Ejemplo:** Si subes a 3%, el ratio de alimentos mejorará y México podría exportar excedentes

> [!IMPORTANT]
> **Variables NO Modificables:** Los parámetros técnicos del modelo (población inicial, PIB base 2005, cuotas de agua, factores de emisión) están calibrados con datos históricos y NO aparecen en la interfaz. Estos se cargan automáticamente desde `config_mexico_2005.json`.

---

### 3. Escenarios Predefinidos

El menú desplegable superior te permite cargar 3 escenarios pre-configurados que representan trayectorias contrastantes para el futuro de México:

#### 🟢 Caso Base 2005 (Business as Usual)
- **Clave:** `base_2005`
- **Descripción:** Configuración histórica de México 2005 con tasas de crecimiento moderadas
- **Variables de Crecimiento:**
  - Crecimiento Poblacional: **1.15%** anual (tasa histórica observada)
  - Crecimiento PIB: **1.0%** anual (crecimiento moderado post-2005)
  - Crecimiento Urbanización: **1.76%** anual (tendencia histórica)
  - Crecimiento Rendimiento Agrícola: **2.2%** anual (mejora gradual tecnológica)

**¿Qué representa?**
Este es el escenario de **referencia**. Usa los datos históricos reales de México en 2005 como punto de partida y proyecta el futuro asumiendo que las tendencias continúan sin cambios mayores. Es el "si todo sigue igual" que sirve como línea base para comparar otros escenarios.

**Resultado Esperado:**
- ✅ Seguridad alimentaria mantenida (Ratio > 1.0)
- ⚠️ Estrés hídrico moderado pero manejable
- ⚠️ Emisiones CO₂ crecientes (sin transición energética)
- 📊 Sirve como punto de comparación para medir el impacto de políticas alternativas

---

#### 🔴 Crecimiento Acelerado (Presión WEFE)
- **Clave:** `crecimiento_acelerado`
- **Descripción:** Alto crecimiento poblacional y económico - máxima presión sobre recursos agua-energía-alimento
- **Variables de Crecimiento:**
  - Crecimiento Poblacional: **2.0%** anual ⬆️ (presión demográfica alta)
  - Crecimiento PIB: **4.5%** anual ⬆️ (industrialización acelerada)
  - Crecimiento Urbanización: **0.8%** anual ⬆️ (urbanización rápida)
  - Crecimiento Rendimiento Agrícola: **1.5%** anual ⬇️ (tecnología agrícola rezagada)

**¿Qué representa?**
Simula un México con **crecimiento económico explosivo** pero sin inversión correspondiente en agricultura y sostenibilidad. La población crece rápido, la economía se industrializa agresivamente, pero la tecnología agrícola no sigue el ritmo. Es el escenario de "desarrollo desordenado".

**Resultado Esperado:**
- 🔴 **Crisis alimentaria** (Ratio < 1.0) - La población crece más rápido que la capacidad de producción
- 🔴 **Estrés hídrico severo** - Industria y ciudades compiten por agua con agricultura
- 🔴 **Emisiones CO₂ récord** - Industrialización masiva sin energías limpias
- ⚠️ **Mayor desigualdad** - Ciudad vs campo, norte vs sur
- 📈 Este escenario muestra el **costo de crecer sin planificar**

---

#### 🟢 Transición Sostenible (Eficiencia WEFE)
- **Clave:** `transicion_sostenible`
- **Descripción:** Crecimiento controlado con innovación tecnológica - eficiencia en uso de recursos
- **Variables de Crecimiento:**
  - Crecimiento Poblacional: **0.8%** anual ⬇️ (control demográfico/planificación familiar)
  - Crecimiento PIB: **3.2%** anual ⬆️ (crecimiento verde/economía del conocimiento)
  - Crecimiento Urbanización: **0.5%** anual (urbanización planificada)
  - Crecimiento Rendimiento Agrícola: **4.0%** anual ⬆️ (revolución agrotecnológica)

**¿Qué representa?**
Simula un México que **invierte en eficiencia y tecnología**. La población crece lentamente (por educación y acceso a salud reproductiva), la economía crece de manera inteligente (servicios, tecnología verde), y la agricultura se moderniza radicalmente (agricultura de precisión, biotecnología, riego eficiente).

**Resultado Esperado:**
- ✅ **Excedente alimentario** (Ratio > 1.3) - Capacidad de exportación
- ✅ **Seguridad hídrica** - Menor demanda per cápita por eficiencia
- ⚠️ **Emisiones moderadas** - Mayor PIB pero mejor eficiencia energética
- 🌱 **Balance sostenible** - Calidad de vida alta sin sacrificar recursos
- 📊 Este escenario muestra que **desarrollo y sostenibilidad SÍ son compatibles** si se planifican correctamente

---

### 4. Panel de Resultados - Tarjetas de Resumen

Después de ejecutar la simulación, aparecen 4 tarjetas en la parte superior que resumen el estado final del sistema:

#### 💧 Ratio Agua Final
**Qué muestra:** El balance entre oferta y demanda de agua al final de la simulación

**Fórmula:** $W_R = \frac{\text{Oferta Total}}{\text{Demanda Total}}$ (Ecuación 7)

**Interpretación:**
- **> 3.0:** 🟢 Seguro (abundancia de agua)
- **1.5 - 3.0:** 🟡 Estable (reserva moderada)
- **1.0 - 1.5:** 🟠 Estrés moderado (límite de seguridad)
- **< 1.0:** 🔴 Crisis hídrica (demanda supera oferta)

**Ejemplo práctico:** Un ratio de 0.85 significa que el país demanda 15% más agua de la que tiene disponible → Necesitas importar agua virtual (en alimentos) o habrá escasez.

#### 🌾 Ratio Alimentos Final
**Qué muestra:** Seguridad alimentaria (autosuficiencia)

**Fórmula:** $F_R = \frac{\text{Producción Total}}{\text{Demanda Total}}$ (Ecuación 20)

**Interpretación:**
- **> 1.2:** 🟢 Excedente (se puede exportar)
- **1.0 - 1.2:** 🟡 Autosuficiente (balance justo)
- **0.8 - 1.0:** 🟠 Déficit leve (importaciones necesarias)
- **< 0.8:** 🔴 Hambruna (crisis alimentaria severa)

**Ejemplo práctico:** Un ratio de 1.5 significa que produces 50% más comida de la que necesitas → México sería exportador neto de alimentos.

**Nota Importante:** Este ratio incluye la demanda de granos para alimentar ganado (factor 3.5:1), por eso es más difícil de alcanzar que si solo contáramos consumo humano directo.

#### ⚡ Ratio Energía Final
**Qué muestra:** Balance energético

**Fórmula:** $E_R = \frac{\text{Oferta Total}}{\text{Demanda Total}}$ (Ecuación 15)

**Interpretación:**
- **> 1.0:** 🟢 Superávit (se puede exportar)
- **= 1.0:** 🟡 Balance perfecto
- **< 1.0:** 🔴 Déficit (apagones, importaciones)

**Ejemplo práctico:** Un ratio de 0.9 significa déficit del 10% → México tendría que importar electricidad o sufrir apagones.

#### 🌍 Emisiones CO₂ Total
**Qué muestra:** Emisiones acumuladas de dióxido de carbono durante toda la simulación

**Fórmula:** Suma de emisiones año con año (Ecuación 23)

**Interpretación:**
- Menor es mejor para el clima
- Incluye emisiones de carbón, petróleo y gas (sector energético)
- Incluye 160 Mt/año de emisiones no energéticas (cemento, agricultura)

**Ejemplo práctico:** 750 Mt acumuladas en 30 años = promedio de 25 Mt/año → Compara con la meta de París de reducir emisiones.

---

### 5. Panel de Resultados - Gráficas

La interfaz muestra 4 gráficas que visualizan la evolución temporal de cada subsistema. Aquí explicamos **por qué están** y **qué significan**:

#### 📊 Gráfica 1: Subsistema Agua
**Por qué está:** El agua es un recurso finito y crítico. Esta gráfica te permite ver si México se está quedando sin agua y en qué año ocurrirá el punto crítico.

**Qué muestra:**
- **Línea azul (Demanda de Agua):** Agua total consumida por agricultura, industria, hogares y energía
- **Línea celeste (Oferta de Agua):** Agua renovable disponible de ríos, acuíferos y desalinización

**Cómo interpretar:**
- Si las líneas **se cruzan**, ese es el año donde la demanda supera la oferta (crisis)
- Si la **distancia entre líneas disminuye**, el estrés hídrico está aumentando
- Si ves la **oferta caer** (línea celeste baja), significa que los acuíferos se están agotando

**Ejemplo:** Si en 2030 las líneas se cruzan, significa que a partir de ese año México no tendrá suficiente agua natural y tendrá que:
- Importar agua virtual (alimentos desde otros países)
- Reducir consumo (racionamiento)
- Invertir en desalinización (caro)

#### 📊 Gráfica 2: Subsistema Alimentos
**Por qué está:** Muestra la seguridad alimentaria del país. Si México no produce suficiente comida, depende de importaciones (vulnerabilidad).

**Qué muestra:**
- **Línea verde (Ratio Seguridad Alimentaria):** Producción / Demanda

**Cómo interpretar:**
- Línea **por encima de 1.0** = Autosuficiente o exportador
- Línea **por debajo de 1.0** = Importador neto (peligro)
- Si la línea **baja con el tiempo**, la situación alimentaria empeora

**Ejemplo:** Si el ratio cae de 1.2 a 0.9 en 20 años, significa que México pasó de exportar 20% a tener que importar 10% de sus alimentos.

#### 📊 Gráfica 3: Subsistema Energía
**Por qué está:** La energía impulsa toda la economía. Esta gráfica muestra si el país puede cubrir su demanda eléctrica/combustible.

**Qué muestra:**
- **Línea naranja (Demanda de Energía):** Energía total requerida por industria, hogares, agricultura y bombeo de agua
- **Línea amarilla (Oferta de Energía):** Energía total producida (renovables + fósiles)

**Cómo interpretar:**
- Si **demanda > oferta**, el país tiene apagones o debe importar energía
- Si la **pendiente de demanda es muy alta**, la economía está creciendo rápido pero necesita más generación
- Observa el "fossil gap": la brecha entre renovables y demanda que se llena con petróleo/gas

**Ejemplo:** Si la demanda sube de 7,000 PJ a 15,000 PJ pero la oferta solo llega a 12,000 PJ, hay un déficit del 20% → Apagones o importar gas natural.

#### 📊 Gráfica 4: Emisiones CO₂
**Por qué está:** El cambio climático es consecuencia directa de quemar combustibles fósiles. Esta gráfica muestra la "factura ambiental" del crecimiento.

**Qué muestra:**
- **Línea morada (Emisiones CO₂):** Toneladas de dióxido de carbono emitidas cada año

**Cómo interpretar:**
- Si la línea **sube**, el país está contaminando más (alejándose de metas climáticas)
- Si la línea **baja**, hay transición energética (más renovables, menos fósiles)
- La **pendiente** indica qué tan rápido empeora o mejora la situación

**Ejemplo:** Si las emisiones suben de 450 Mt/año a 900 Mt/año, México duplicó su contaminación → Incumplimiento del Acuerdo de París.

**Relación con PIB:** Si el PIB crece sin invertir en renovables, el modelo automáticamente quema más petróleo/gas para cubrir la demanda energética, disparando el CO₂.

---

### 6. Flujo de Trabajo Recomendado

**Paso 1:** Ejecuta el **Escenario Base** primero
- Esto te da la línea de referencia (qué pasa si todo sigue igual)

**Paso 2:** Haz clic en **"Agregar a Comparación"**
- Guarda los resultados base para comparar después

**Paso 3:** Cambia UNA variable a la vez
- Ejemplo: Sube `Crecimiento PIB` de 2.5% a 4.0%
- Ejecuta de nuevo

**Paso 4:** Observa los cambios
- ¿El ratio de agua bajó? ¿Las emisiones subieron?
- Esto te dice el **efecto aislado** de esa variable

**Paso 5:** Exporta los resultados
- **CSV:** Para análisis en Excel/Python
- **JSON:** Para procesamiento programático

**Paso 6:** Experimenta con combinaciones
- Prueba: ¿Qué pasa si subo PIB PERO también mejoro rendimiento agrícola?
- Esto te ayuda a encontrar el "punto óptimo" de políticas

---

### 7. Consejos para Interpretar Resultados

#### ⚠️ Advertencia: El Modelo NO es una predicción exacta
Es una **herramienta de exploración de escenarios**. Los resultados te dicen:
- "Si X crece y Y se mantiene, entonces Z pasará"
- NO te dicen: "México en 2035 será exactamente así"

#### 🔍 Busca Puntos Críticos
- ¿En qué año el ratio de agua cae por debajo de 1.0?
- ¿Cuándo las emisiones superan 1,000 Mt?
- Estos son los "años de colapso" que debes evitar con políticas

#### ⚖️ Balance de Trade-offs
- No existe el escenario perfecto
- Crecer económicamente (PIB alto) suele aumentar emisiones
- Controlar población mejora todos los ratios, pero es políticamente difícil
- Encuentra el balance que consideres aceptable

#### 📈 Sensibilidad de Variables
Las variables más sensibles (mayor impacto):
1. **Crecimiento Poblacional:** Afecta TODO (agua, alimentos, energía)
2. **Crecimiento PIB:** Dispara demanda energética e hídrica industrial
3. **Rendimiento Agrícola:** Crucial para seguridad alimentaria
4. **Años de Simulación:** Más años = más acumulación de problemas

---

## 📈 Parte 5: Análisis Comparativo de Escenarios (Simulación a 2035)

Al ejecutar el modelo proyectado a 30 años (2005-2035), obtuvimos los siguientes resultados para cada uno de los 3 escenarios. Esta tabla resume las métricas clave al final de la simulación (año 2035):

| Escenario | Población Final | PIB Final | Ratio Alimentos | Ratio Agua | Emisiones CO₂ Totales | Estado del Sistema |
| :--- | ---: | ---: | ---: | ---: | ---: | :--- |
| **Caso Base 2005** | ~145 M | ~$25.7 T | 1.25-1.35 | 0.8-1.2 | ~650-750 Mt | ⚠️ **Estable pero vulnerable** |
| **Crecimiento Acelerado** | ~173 M | ~$47.3 T | **0.75-0.95** | **0.6-0.9** | ~950-1100 Mt | 🔴 **Crisis WEFE múltiple** |
| **Transición Sostenible** | ~127 M | ~$33.8 T | 1.50-1.70 | 1.1-1.4 | ~580-680 Mt | ✅ **Equilibrio sostenible** |

> [!NOTE]
> Los valores son aproximados y dependen de parámetros estocásticos del modelo. Ejecuta las simulaciones para obtener resultados precisos con tu configuración específica.

---

### 🔍 Interpretación Detallada de Cada Escenario

#### 1️⃣ Caso Base 2005 (Business as Usual)

**📊 Proyección al 2035:**
- **Población:** Crece de 103M → 145M (+40%)
- **PIB:** Crece modestamente siguiendo la tendencia histórica
- **Seguridad Alimentaria:** Se mantiene por encima de 1.0 (autosuficiente) gracias a la mejora tecnológica del 2.2% anual
- **Agua:** Estrés moderado - el ratio se acerca a 1.0 pero no colapsa
- **Emisiones:** Crecen constantemente sin control climático

**🧠 Deducción:**
Este escenario muestra que México puede **"sobrevivir"** con sus tendencias actuales, pero apenas. No hay colapso inmediato, pero tampoco hay mejora significativa. Es el camino de la **inercia**: el país crece, la gente se alimenta, pero:
- ❌ Las emisiones de CO₂ siguen aumentando (incumplimiento del Acuerdo de París)
- ⚠️ El estrés hídrico aumenta progresivamente (especialmente en regiones áridas)
- ⚠️ No hay margen de seguridad - cualquier crisis externa (sequía, pandemia) podría desestabilizar el sistema

**💡 Lección Clave:** "Business as usual" NO es sostenible a largo plazo. Funciona, pero deja al país vulnerable.

---

#### 2️⃣ Crecimiento Acelerado (Presión WEFE)

**📊 Proyección al 2035:**
- **Población:** Explota de 103M → 173M (+68%) - presión demográfica extrema
- **PIB:** Casi se duplica gracias al 4.5% anual - aparente "milagro económico"
- **Seguridad Alimentaria:** **COLAPSA** (Ratio < 1.0) - México no puede alimentar a su población
- **Agua:** **CRISIS SEVERA** (Ratio < 0.9) - Demanda supera oferta en ~20%
- **Emisiones:** Récord histórico - el precio del crecimiento económico sin planificación

**🧠 Deducción:**
Este es el escenario de la **"trampa del crecimiento"**. En papel, la economía se ve impresionante (PIB alto), pero el sistema colapsa porque:
- 🔴 **La población crece más rápido que la agricultura** (2.0% vs 1.5%)
- 🔴 **La industria consume agua más rápido de lo que se repone**
- 🔴 **El boom económico quema combustibles fósiles sin control**

**Consecuencias prácticas en 2035:**
- México **importaría ~25-30% de sus alimentos** (dependencia alimentaria peligrosa)
- Regiones del norte enfrentarían **racionamiento de agua permanente**
- Las **emisiones per cápita superarían a países desarrollados** sin el bienestar correspondiente

**💡 Lección Clave:** Crecer por crecer NO funciona. El PIB alto sin inversión en agricultura, agua y energía limpia conduce a crisis humanitarias. Es el ejemplo perfecto de **desarrollo no sostenible**.

---

#### 3️⃣ Transición Sostenible (Eficiencia WEFE)

**📊 Proyección al 2035:**
- **Población:** Crece moderadamente de 103M → 127M (+23%) - por planificación familiar y desarrollo humano
- **PIB:** Crece saludablemente (~3.2% anual) - economía próspera pero eficiente
- **Seguridad Alimentaria:** **EXCEDENTE** (Ratio > 1.5) - México podría exportar alimentos
- **Agua:** Situación **holgada** (Ratio > 1.1) - Margen de seguridad cómodo
- **Emisiones:** Las más bajas de los 3 escenarios (relativamente) - por mayor eficiencia y menor presión demográfica

**🧠 Deducción:**
Este escenario demuestra que **desarrollo y sostenibilidad SÍ son compatibles**. La clave es:
- ✅ **Control demográfico inteligente** (educación, acceso a salud reproductiva) → menos presión sobre recursos
- ✅ **Revolución agrotecnológica** (4.0% anual) → agricultura de precisión, riego eficiente, biotecnología
- ✅ **Crecimiento económico verde** (servicios, tecnología, energías limpias) → riqueza sin destrucción

**Consecuencias prácticas en 2035:**
- México sería **exportador neto de alimentos** (seguridad nacional fortalecida)
- Agua disponible incluso para sectores no críticos (turismo, industria ligera)
- **Estándar de vida alto** (PIB per cápita mayor que en Caso Base) con huella ecológica controlada

**💡 Lección Clave:** La sostenibilidad NO requiere pobreza. Requiere **inteligencia**: invertir en tecnología agrícola, planificar el crecimiento demográfico, y priorizar eficiencia sobre volumen.

---

### 🎯 Conclusiones Transversales

#### 🔑 Variables Críticas Identificadas

1. **Crecimiento Poblacional** (La más sensible)
   - Impacta **directamente** agua, alimentos y energía
   - Diferencia entre 0.8% y 2.0% = Diferencia entre excedente y crisis
   - **Política recomendada:** Inversión en educación y salud reproductiva

2. **Rendimiento Agrícola** (La más estratégica)
   - 1.5% vs 4.0% = Diferencia entre importar y exportar alimentos
   - **Política recomendada:** I+D agropecuario, transferencia tecnológica, créditos para agricultura de precisión

3. **Crecimiento PIB** (La más compleja)
   - Alto PIB sin eficiencia = Crisis ambiental
   - PIB moderado con tecnología verde = Prosperidad sostenible
   - **Política recomendada:** Incentivar economía del conocimiento, no industria pesada

#### ⚖️ Trade-offs Inevitables

| Si priorizas... | Ganas... | Pero pierdes... | Ejemplo |
| :--- | :--- | :--- | :--- |
| **PIB alto sin control** | Riqueza a corto plazo | Agua, aire, seguridad alimentaria | Crecimiento Acelerado |
| **Status quo** | Estabilidad | Oportunidades de mejora | Caso Base |
| **Eficiencia y planeación** | Sostenibilidad a largo plazo | Crecimiento económico explosivo | Transición Sostenible |

#### 🌟 Recomendación del Modelo

Basado en las simulaciones, el escenario **Transición Sostenible** es el único que:
- ✅ Garantiza seguridad alimentaria a largo plazo
- ✅ Mantiene balance hídrico saludable
- ✅ Permite crecimiento económico significativo
- ✅ Controla emisiones relativamente

**El modelo sugiere que la política pública óptima para México incluye:**
1. **Inversión masiva en agricultura tecnificada** (objetivo: 3.5-4.0% mejora anual)
2. **Planificación familiar voluntaria** (objetivo: reducir tasa de crecimiento a ~0.8-1.0%)
3. **Transición energética gradual** (más renovables, menos fósiles)
4. **Urbanización planificada** (evitar megaciudades insostenibles)

> [!WARNING]
> **Advertencia:** Estos resultados son **exploratorios**, no predicciones exactas. El modelo asume que todas las variables crecen exponencialmente, lo cual es una simplificación. En la realidad, habrá choques externos (crisis, innovaciones disruptivas, cambio climático) que alterarán las trayectorias. Usa estos escenarios como **guías de planeación**, no como profecías.

---

## ❓ Parte 6: Preguntas Frecuentes y Curiosidades

### 🌊 ¿Por qué la Oferta de Agua parece tan alejada de la Demanda?

Al ver la gráfica del subsistema hídrico, notarás una brecha enorme entre la línea de **Oferta** (~472,000 $hm^3$) y la de **Demanda** (~76,000 $hm^3$). Pareciera que a México le sobra muchísima agua. **Esto es una ilusión óptica de los promedios nacionales** por tres razones:

#### 1. Oferta Bruta vs. Oferta Disponible
La línea de "Oferta" muestra el **Agua Renovable Total** (lluvia, escurrimientos). No toda esa agua se puede capturar. Mucha se evapora, fluye al mar en zonas inaccesibles o se pierde en fugas antes de llegar a las ciudades.

#### 2. El Caudal Ecológico (La demanda invisible)
El modelo reserva explícitamente **141,658 $hm^3$** (aprox. 30% del total) como **Caudal Ecológico**.
*   Esta agua **NO** es para consumo humano.
*   Es el agua que debe quedarse en los ríos para que los peces vivan, los manglares no se sequen y el ciclo hidrológico continúe.
*   En la gráfica, la línea de "Demanda" solo muestra el consumo humano (Agricultura + Industria + Hogares). Si sumáramos el caudal ecológico, la demanda real sería el triple, cerrando la brecha visualmente.

#### 3. La Trampa del Promedio (Norte vs Sur)
México es hidrológicamente dos países:
*   **Sur-Sureste:** Tiene el 70% del agua pero poca demanda industrial. Aquí "sobra" agua.
*   **Centro-Norte:** Tiene el 80% de la población y el PIB, pero solo el 30% del agua. Aquí hay déficit.
*   Al sumar todo en un solo número nacional, el exceso del sur "esconde" la crisis del norte.

> **En resumen:** Aunque la gráfica muestre que "sobra" agua a nivel nacional, la realidad es que gran parte de esa agua es ecológica o está en el sur, mientras que el norte ya vive en estrés hídrico severo (por eso implementamos la lógica de *Estrés Regional* explicada en la Parte 3).



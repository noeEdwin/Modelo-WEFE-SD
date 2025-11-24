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

El menú desplegable superior te permite cargar 4 escenarios pre-configurados:

#### 🟢 Escenario Base (2005)
- **Descripción:** Tendencia histórica "Business as Usual"
- **Variables:** 
  - Población: 1.15%
  - PIB: 2.5%
  - Urbanización: 0.4%
  - Rendimiento agrícola: 2.2%
- **Interpretación:** Continuar como vamos. Refleja el pasado reciente de México.

#### 🚀 Escenario Optimista + Tecnológico
- **Descripción:** Alto crecimiento económico con innovación
- **Variables:**
  - Población: 1.0% (menor, por desarrollo)
  - PIB: 4.0% ⬆️ (economía fuerte)
  - Urbanización: 0.6% ⬆️
  - Rendimiento agrícola: 3.5% ⬆️ (tecnología avanzada)
- **Resultado Esperado:** Excedente de alimentos, pero emisiones de CO₂ récord si no hay transición energética

#### 📉 Escenario Pesimista + Crisis
- **Descripción:** Estancamiento económico con sobrepoblación
- **Variables:**
  - Población: 1.8% ⬆️ (alta natalidad)
  - PIB: 1.2% ⬇️ (crisis económica)
  - Urbanización: 0.2% ⬇️
  - Rendimiento agrícola: 0.8% ⬇️ (poca inversión)
- **Resultado Esperado:** ⚠️ Crisis alimentaria (Ratio < 1.0), estrés hídrico, pero bajas emisiones por pobreza

#### 🌱 Escenario Sostenible + Verde
- **Descripción:** Balance entre desarrollo y sustentabilidad
- **Variables:**
  - Población: 0.8% ⬇️ (planificación familiar)
  - PIB: 2.8% (crecimiento moderado)
  - Urbanización: 0.5%
  - Rendimiento agrícola: 3.0% ⬆️ (agricultura de precisión)
- **Resultado Esperado:** Equilibrio entre bienestar económico y presión sobre recursos

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


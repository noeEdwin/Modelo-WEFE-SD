# Documentación del Proyecto: Modelo WEFE (Agua-Energía-Alimentos-Ecología)

Este proyecto simula la interacción entre cuatro sistemas críticos para la sociedad: **Agua, Energía, Alimentos y Ecología**. El objetivo es entender cómo el consumo en un sector afecta a los otros y predecir posibles crisis o desequilibrios en el futuro (por ejemplo, escasez de agua o altas emisiones de CO2).

## 📖 Explicación Sencilla (Para no expertos)

Imagina que el país es un gran sistema donde todo está conectado. No podemos producir alimentos sin agua, no podemos mover esa agua sin energía, y producir esa energía a menudo contamina el medio ambiente. Este modelo matemático ("WEFE") calcula año tras año cómo cambian estos recursos.

### 1. 💧 Subsistema de Agua
**¿Qué calculamos?**
Simplemente comparamos el **Agua que tenemos** (oferta) contra el **Agua que necesitamos** (demanda).
*   **La Demanda:** Sumamos toda el agua que usan las casas, las fábricas, los campos de cultivo y las plantas de energía.
*   **La Oferta:** Es el agua disponible en ríos y acuíferos.
*   **El Resultado:** Si necesitamos más agua de la que hay disponible, tenemos "Estrés Hídrico". El modelo nos avisa si estamos en peligro de quedarnos sin agua.

### 2. ⚡ Subsistema de Energía
**¿Qué calculamos?**
Calculamos cuánta energía necesita el país para funcionar y cómo la producimos.
*   **La Demanda:** Energía para hogares, industrias y para bombear agua.
*   **La Oferta:** Primero usamos energías limpias (renovables). Si no es suficiente, "quemamos" combustibles fósiles (carbón, petróleo, gas) para cubrir el resto.
*   **La Conexión:** Si usamos más combustibles fósiles, aumentamos la contaminación (CO2).

### 3. 🍎 Subsistema de Alimentos
**¿Qué calculamos?**
Verificamos si producimos suficiente comida para toda la población.
*   **La Demanda:** Calculamos cuánto come cada persona (granos, verduras, carne). *Ojo:* Para producir carne, los animales también necesitan comer granos (forraje), así que eso también lo sumamos.
*   **La Oferta:** Depende de cuánta tierra cultivamos y qué tan eficiente es la cosecha.
*   **El Resultado:** Vemos si el país es autosuficiente o si le falta comida.

### 4. 🌳 Subsistema de Ecología
**¿Qué calculamos?**
Es el "costo ambiental" de todo lo anterior.
*   **Emisiones (CO2):** Salen principalmente de quemar carbón, petróleo y gas en el sector de energía.
*   **Contaminación del Agua:** Calculamos cuánta agua sucia sale de las ciudades.

---

## 🔬 Detalles Técnicos y Ecuaciones (Para expertos)

A continuación se describe cómo el código (`wefe_model.py`) traduce las fórmulas matemáticas científicas (basadas en *Ling et al., 2024*) a instrucciones de programación.

### 1. Subsistema de Agua (Water Subsystem)
**Ecuación Teórica:** $WD = WD_{agriculture} + WD_{industry} + WD_{domestic} + WD_{energy}$
*   **En el código:** Sumamos el consumo de cada sector.
    ```python
    wd_human = wd_agri + wd_ind + wd_dom + wd_energy
    ```
*   **Balance ($W_R$):** Es la división entre Agua Disponible / Demanda Humana.
    ```python
    w_r = ws_available / wd_human
    ```

### 2. Subsistema de Energía (Energy Subsystem)
**Ecuación Teórica:** $ED = \sum ED_{sectores}$
*   **En el código:**
    ```python
    total_ed = ed_ind + ed_dom + ed_water + ed_agri
    ```
*   **Oferta ($ES$):** El código llena el hueco de demanda primero con renovables y luego con fósiles.
    ```python
    fossil_gap = total_ed - supply_renewables
    # Si falta energía, usamos carbón, petróleo y gas proporcionalmente
    ```

### 3. Subsistema de Alimentos (Food Subsystem)
**Ecuación Teórica:** $FD = P \times FD_{per-capita}$
*   **En el código:** Multiplicamos la población por la dieta promedio.
    ```python
    fd_grains_human = s['population'] * p['diet_grains_per_capita']
    ```
*   **Nota Técnica:** Se agregó explícitamente la demanda de alimento para ganado (feed), que es vital para calcular la demanda real de granos.

### 4. Subsistema de Ecología (Ecology Subsystem)
**Ecuación Teórica:** $CO_2 = \sum (Energía \times FactorEmisión)$
*   **En el código:**
    ```python
    total_co2 = (carbón * factor_c) + (petróleo * factor_p) + (gas * factor_g)
    ```

### Resumen de Variables Clave

| Concepto | Variable en Paper | Variable en Python |
| :--- | :--- | :--- |
| Demanda de Agua | $WD$ | `wd_human` |
| Balance Hídrico | $W_R$ | `water_ratio` |
| Demanda de Energía | $ED$ | `total_ed` |
| Emisiones de CO2 | $CO_2$ | `total_co2` |
| Oferta de Alimentos | $FS$ | `total_fs` |

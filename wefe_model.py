import pandas as pd

class WEFEModel:
    def __init__(self, initial_data, params, scenarios):
        """
        Inicializa el modelo WEFE con los datos base y coeficientes.
        
        :param initial_data: Diccionario con valores del año base (Stocks iniciales).
        :param params: Diccionario con coeficientes técnicos (Factores de emisión, cuotas).
        :param scenarios: Diccionario con tasas de cambio anuales (Variables de decisión).
        """
        self.state = initial_data.copy()
        self.params = params
        self.scenarios = scenarios
        self.current_year = initial_data['year']
        self.history = []

    def _calculate_social_economic(self):
        """
        Paso 0: Actualizar conductores macro (Población, PIB, Urbanización).
        [cite_start]Cita PDF: Secciones 2.3.5 y 2.4 [cite: 416, 425]
        """
        # Tasas de crecimiento definidas en el escenario
        self.state['population'] *= (1 + self.scenarios.get('growth_pop', 0))
        self.state['gdp'] *= (1 + self.scenarios.get('growth_gdp', 0))
        self.state['urbanization_rate'] += self.scenarios.get('growth_urbanization', 0)
        
        # Crecimiento tecnológico en agricultura (Rendimientos)
        growth_yield = self.scenarios.get('growth_agri_yield', 0)
        self.state['yield_grains'] *= (1 + growth_yield)
        self.state['yield_veggies'] *= (1 + growth_yield)
        self.state['yield_fruits'] *= (1 + growth_yield)
        self.state['yield_meat'] *= (1 + growth_yield)
        self.state['yield_poultry'] *= (1 + growth_yield)
        self.state['yield_dairy'] *= (1 + growth_yield)

    def _step_food(self):
        """
        [cite_start]Subsistema de Alimentos: Ecuaciones 16-20 [cite: 362-377]
        Calcula demanda y oferta para 5 categorías clave + ganadería.
        """
        s = self.state
        p = self.params
        
        # --- DEMANDA HUMANA (Directa) ---
        fd_grains_human = s['population'] * p['diet_grains_per_capita']
        fd_veggies = s['population'] * p['diet_veggies_per_capita']
        fd_fruits = s['population'] * p['diet_fruits_per_capita']
        fd_meat = s['population'] * (p['diet_red_meat_per_capita'] + p['diet_white_meat_per_capita'])
        fd_dairy = s['population'] * p['diet_dairy_per_capita']

        # --- DEMANDA GANADERA (Indirecta - Feed) ---
        # Asumimos conversión: kg grano / kg carne. 
        # Promedios globales: Res ~7:1, Pollo ~2:1, Cerdo ~4:1.
        # Simplificación: Factor ponderado ~3.5 para carne total y ~1.2 para lácteos
        factor_feed_meat = 3.5
        factor_feed_dairy = 1.2
        
        # La demanda de carne impulsa la demanda de granos forrajeros
        fd_feed_meat = fd_meat * factor_feed_meat
        fd_feed_dairy = fd_dairy * factor_feed_dairy
        
        total_feed_demand = fd_feed_meat + fd_feed_dairy
        
        # Demanda Total de Granos = Consumo Humano + Forraje
        fd_grains_total = fd_grains_human + total_feed_demand

        total_fd = fd_grains_total + fd_veggies + fd_fruits + fd_meat + fd_dairy
        
        # --- OFERTA (FS) ---
        fs_grains = s['area_grains'] * s['yield_grains']
        fs_veggies = s['area_veggies'] * s['yield_veggies']
        fs_fruits = s['area_fruits'] * s['yield_fruits']
        fs_meat = (s['heads_cows'] * s['yield_meat']) + (s['heads_poultry'] * s['yield_poultry'])
        fs_dairy = s['heads_dairy'] * s['yield_dairy']
        
        total_fs = fs_grains + fs_veggies + fs_fruits + fs_meat + fs_dairy
        
        return {
            'food_demand_total': total_fd,
            'food_supply_total': total_fs,
            'food_ratio': total_fs / total_fd if total_fd > 0 else 0,
            'production_grains': fs_grains,
            'feed_demand': total_feed_demand
        }

    def _step_water(self, food_metrics):
        """
        [cite_start]Subsistema de Agua: Ecuaciones 1-7 [cite: 323-348]
        """
        s = self.state
        p = self.params
        
        # --- DEMANDA CONSUNTIVA (Humana) ---
        # Eq 2: Agricultura
        wd_agri = (s['area_grains'] + s['area_veggies'] + s['area_fruits']) * p['quota_water_crop']
        
        # Eq 3: Industria
        wd_ind = s['gdp'] * p['quota_water_ind']
        
        # Eq 4: Doméstico
        wd_dom = s['population'] * p['quota_water_dom']
        
        # Eq 5: Energía
        wd_energy = s['energy_production_total'] * p['quota_water_energy']
        
        # Total Demanda Humana (Consuntiva)
        wd_human = (wd_agri + wd_ind + wd_dom + wd_energy) / 1000000.0
        
        # --- REQUERIMIENTO ECOLÓGICO (Eq 1) ---
        # El paper (Ling et al., 2024) suma la demanda ecológica a la demanda total.
        wd_eco = s.get('wd_eco_req', 0)
        
        # Demanda Total = Demanda Humana + Demanda Ecológica
        wd_total = wd_human + wd_eco

        # --- OFERTA DISPONIBLE (WS) (Eq 6) ---
        # Oferta Total Natural (Bruta)
        total_ws_natural = s['ws_surface'] + s['ws_ground'] + s['ws_unconventional']
        
        # --- BALANCE (Wr) (Eq 7) ---
        # Ratio = Oferta Total / Demanda Total
        # Nota: Al incluir wd_eco en la demanda, usamos la oferta bruta para el ratio.
        w_r = total_ws_natural / wd_total if wd_total > 0 else 0
        
        return {
            'water_demand': wd_human,     # Reportamos solo humana para coincidir con gráfica SQL (76k)
            'water_supply': total_ws_natural, # Reportamos oferta bruta para coincidir con SQL (472k)
            'water_ratio': w_r,
            'wd_eco': wd_eco,
            'wd_total_system': wd_total   # Guardamos el total real por si acaso
        }

    def _step_energy(self, water_metrics, food_metrics):
        """
        [cite_start]Subsistema de Energía: Ecuaciones 8-15 [cite: 352-396]
        """
        s = self.state
        p = self.params
        
        # --- DEMANDA (ED) ---
        # Eq 9-11: Sectores
        ed_ind = s['gdp'] * p['intensity_energy_ind']
        ed_dom = s['population'] * p['intensity_energy_dom']
        
        # Eq 12: Energía para agua
        ed_water = water_metrics['water_demand'] * p['energy_per_m3_water']
        
        # Eq 9 (Food): Energía para agricultura (tractores, etc.)
        ed_agri = food_metrics['food_supply_total'] * p.get('energy_intensity_agri', 0)
        
        total_ed = ed_ind + ed_dom + ed_water + ed_agri

        # --- OFERTA (ES) ---
        # Eq 13: Fósiles + Renovables (Ahora dinámico)
        # 1. Calculamos primero la oferta renovable disponible
        # Eq 14: Bioenergía (Paja de cultivos)
        bioenergy = food_metrics['production_grains'] * p.get('straw_energy_factor', 0)
        supply_renewables = s['es_renewables'] + bioenergy

        # 2. Calculamos el déficit que deben cubrir los fósiles
        # Gap = Demanda Total - Renovables
        fossil_gap = total_ed - supply_renewables

        # 3. Si hay déficit, lo llenamos con fósiles manteniendo el mix de 2005
        # Ratios dinámicos basados en el estado inicial (config)
        if fossil_gap > 0:
            # Calcular ratios actuales basados en el consumo del año anterior (o inicial)
            # Si es el primer paso, usa los del config.
            # Para mantener la proporción fija del año base:
            base_coal = self.state.get('es_coal_base', self.state['es_coal'])
            base_oil = self.state.get('es_oil_base', self.state['es_oil'])
            base_gas = self.state.get('es_gas_base', self.state['es_gas'])
            
            total_fossil_base = base_coal + base_oil + base_gas
            
            if total_fossil_base > 0:
                ratio_coal = base_coal / total_fossil_base
                ratio_oil = base_oil / total_fossil_base
                ratio_gas = base_gas / total_fossil_base
            else:
                # Fallback si no hay datos base
                ratio_coal = 0.05
                ratio_oil = 0.60
                ratio_gas = 0.35
            
            s['es_coal'] = fossil_gap * ratio_coal
            s['es_oil'] = fossil_gap * ratio_oil
            s['es_gas'] = fossil_gap * ratio_gas
        else:
            # Si sobran renovables (futuro utópico), apagamos fósiles
            s['es_coal'] = 0
            s['es_oil'] = 0
            s['es_gas'] = 0

        total_es = s['es_coal'] + s['es_oil'] + s['es_gas'] + supply_renewables
        
        # --- BALANCE (Er) ---
        # Eq 15
        e_r = total_es / total_ed if total_ed > 0 else 0
        
        return {
            'energy_demand': total_ed, 
            'energy_supply': total_es, 
            'energy_ratio': e_r,
            'consumption_coal': s['es_coal'], 
            'consumption_oil': s['es_oil'],
            'consumption_gas': s['es_gas']
        }

    def _step_ecology(self, energy_metrics):
        """
        [cite_start]Subsistema de Ecología: Ecuaciones 21-24 [cite: 398-409]
        """
        s = self.state
        p = self.params
        
        # --- CO2 (Eq 23-24) ---
        # Emisiones = Consumo (PJ) * Factor (kg/TJ)
        # 1 PJ = 1000 TJ
        # Resultado en kg, dividimos entre 1000 para Toneladas
        
        co2_coal = energy_metrics['consumption_coal'] * p['emission_factor_coal']
        co2_oil = energy_metrics['consumption_oil'] * p['emission_factor_oil']
        co2_gas = energy_metrics['consumption_gas'] * p.get('emission_factor_gas', 0)
        
        # Convertimos de Toneladas a Megatoneladas (Mt)
        total_co2_energy = (co2_coal + co2_oil + co2_gas) / 1000000.0
        
        # Sumamos emisiones de otros sectores (No energéticos: Agricultura, Desechos, Industrial)
        # Ajuste de calibración para igualar el total nacional
        total_co2 = total_co2_energy + p.get('co2_non_energy', 0)
        
        # --- COD (Eq 21-22) ---
        # Contaminación del agua
        wastewater = (s['population'] * p['quota_water_dom']) * 0.8
        total_cod = wastewater * p['pollutant_concentration_dom']
        
        return {'total_co2': total_co2, 'total_cod': total_cod}

    def run(self, years=10):
        """Ejecuta la simulación principal"""
        # print(f"Iniciando simulación desde {self.current_year}...")
        
        for _ in range(years):
            self._calculate_social_economic()
            
            food_res = self._step_food()
            water_res = self._step_water(food_res)
            energy_res = self._step_energy(water_res, food_res)
            eco_res = self._step_ecology(energy_res)
            
            year_data = {'year': self.current_year}
            year_data.update(self.state)
            year_data.update(food_res)
            year_data.update(water_res)
            year_data.update(energy_res)
            year_data.update(eco_res)
            
            self.history.append(year_data)
            
            # Actualización de stocks dependientes de recursos (Feedback)
            # Opción A: Estrés Hídrico Regional (Aggregation Bias Fix)
            # Aunque el promedio nacional (Ratio) sea > 1.0, asumimos que si es < 3.0
            # ya existen regiones críticas sobreexplotando acuíferos.
            if water_res['water_ratio'] < 3.0:
                # No restamos el déficit nacional (que es negativo o cero),
                # sino un "Factor de Estrés Regional" muy suave.
                # Antes: 0.20 (20%) -> Causaba colapso irreal.
                # Ahora: 0.005 (0.5%) -> Simula degradación lenta y realista.
                factor_regional = 0.005
                extraccion_insostenible = water_res['water_demand'] * factor_regional
                self.state['ws_ground'] -= extraccion_insostenible
                
                # Evitar valores negativos (Acuífero agotado)
                if self.state['ws_ground'] < 0:
                    self.state['ws_ground'] = 0
            
            self.current_year += 1
            self.state['year'] = self.current_year
            
        return pd.DataFrame(self.history)

    def calibrar(self, datos_reales_df):
        """
        Compara simulación vs realidad (Validación histórica).
        [cite_start][cite: 460-463] (Ecuación 25: Error relativo)
        """
        # Ejecutamos el modelo por la misma cantidad de años que tenemos en la BD
        years_to_sim = len(datos_reales_df)
        simulacion = self.run(years=years_to_sim)
        
        errores = {}
        print("\n--- REPORTE DE CALIBRACIÓN (Simulación vs. Base de Datos) ---")
        
        # MAPEO CLAVE: 
        # Izquierda: Nombre de variable en tu simulación (Python)
        # Derecha: Nombre exacto de la columna en tu Base de Datos (PostgreSQL)
        mapa_vars = {
            'water_demand':      'demanda_agua_total',
            'total_co2':         'emisiones_co2_real',
            # Sumamos las producciones reales para comparar con el total simulado
            'food_supply_total': ['prod_granos_real', 'prod_hortalizas_real', 'prod_frutas_real', 'prod_carne_real', 'prod_lacteos_real'] 
        }
        
        for var_sim, var_db in mapa_vars.items():
            # Obtenemos valores simulados
            val_sim = simulacion[var_sim].values
            
            # Obtenemos valores reales (Manejando si es una columna única o suma de varias)
            if isinstance(var_db, list):
                # Si es una lista (Alimentos), sumamos las columnas de la BD
                val_real = datos_reales_df[var_db].sum(axis=1).values
            else:
                # Si es una sola columna (Agua, CO2)
                val_real = datos_reales_df[var_db].values
            
            # Cálculo del Error (Ecuación 25 del paper)
            # Evitamos división por cero
            val_real_safe = val_real.copy()
            val_real_safe[val_real_safe == 0] = 1 
            
            error = abs((val_sim - val_real) / val_real_safe).mean() * 100
            errores[var_sim] = error
            
            estado = "✅ OK" if error <= 5.0 else "⚠️ AJUSTAR"
            print(f"Variable: {var_sim:<20} | Error Promedio: {error:.2f}% -> {estado}")
        
        return errores
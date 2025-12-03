import pandas as pd

class WEFEModel:
    def __init__(self, initial_data, params, scenarios):
        """Inicializa el modelo WEFE con los datos base y coeficientes."""
        self.state = initial_data.copy()
        self.params = params
        self.scenarios = scenarios
        self.current_year = initial_data['year']
        self.history = []

    def _calculate_social_economic(self):
        """Actualizo conductores macro (Población, PIB, Urbanización)."""
        self.state['population'] *= (1 + self.scenarios.get('growth_pop', 0))
        self.state['gdp'] *= (1 + self.scenarios.get('growth_gdp', 0))
        self.state['urbanization_rate'] += self.scenarios.get('growth_urbanization', 0)
        
        growth_yield = self.scenarios.get('growth_agri_yield', 0)
        self.state['yield_grains'] *= (1 + growth_yield)
        self.state['yield_veggies'] *= (1 + growth_yield)
        self.state['yield_fruits'] *= (1 + growth_yield)
        self.state['yield_meat'] *= (1 + growth_yield)
        self.state['yield_poultry'] *= (1 + growth_yield)
        self.state['yield_dairy'] *= (1 + growth_yield)

    def _step_food(self):
        """Calculo demanda y oferta para 5 categorías clave + ganadería."""
        s = self.state
        p = self.params
        
        fd_grains_human = s['population'] * p['diet_grains_per_capita']
        fd_veggies = s['population'] * p['diet_veggies_per_capita']
        fd_fruits = s['population'] * p['diet_fruits_per_capita']
        fd_meat = s['population'] * (p['diet_red_meat_per_capita'] + p['diet_white_meat_per_capita'])
        fd_dairy = s['population'] * p['diet_dairy_per_capita']

        # Asumo conversión kg grano / kg carne: Res ~7:1, Pollo ~2:1, Cerdo ~4:1
        factor_feed_meat = 3.5
        factor_feed_dairy = 1.2
        
        fd_feed_meat = fd_meat * factor_feed_meat
        fd_feed_dairy = fd_dairy * factor_feed_dairy
        
        total_feed_demand = fd_feed_meat + fd_feed_dairy
        fd_grains_total = fd_grains_human + total_feed_demand

        total_fd = fd_grains_total + fd_veggies + fd_fruits + fd_meat + fd_dairy
        
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
        """Calculo demanda y oferta de agua."""
        s = self.state
        p = self.params
        
        wd_agri = (s['area_grains'] + s['area_veggies'] + s['area_fruits']) * p['quota_water_crop']
        wd_ind = s['gdp'] * p['quota_water_ind']
        wd_dom = s['population'] * p['quota_water_dom']
        wd_energy = s['energy_production_total'] * p['quota_water_energy']
        
        # Ajusto por uso no registrado
        factor_unregistered_agri = p.get('factor_unregistered_agri', 1.50)
        factor_unregistered_ind = p.get('factor_unregistered_ind', 1.20)      
        factor_unregistered_dom = p.get('factor_unregistered_dom', 1.30)      
        factor_unregistered_energy = p.get('factor_unregistered_energy', 1.10) 
        
        wd_agri_real = wd_agri * factor_unregistered_agri
        wd_ind_real = wd_ind * factor_unregistered_ind
        wd_dom_real = wd_dom * factor_unregistered_dom
        wd_energy_real = wd_energy * factor_unregistered_energy
        
        wd_human = (wd_agri_real + wd_ind_real + wd_dom_real + wd_energy_real) / 1000000.0
        
        wd_eco = s.get('wd_eco_req', 0)
        wd_total = wd_human + wd_eco

        total_ws_natural = s['ws_surface'] + s['ws_ground'] + s['ws_unconventional']
        
        # Aplico factor de oferta efectiva 0.429 (43%) - representa el agua realmente utilizable
        factor_oferta_efectiva = 0.429
        ws_effective = total_ws_natural * factor_oferta_efectiva
        
        # Uso wd_human en el denominador porque ws_effective YA descuenta el caudal ecológico
        w_r = ws_effective / wd_human if wd_human > 0 else 0
        
        return {
            'water_demand': wd_human,     
            'water_supply': ws_effective,
            'water_ratio': w_r,
            'wd_eco': wd_eco,
            'wd_total_system': wd_total,
            'ws_potential_climate': total_ws_natural
        }

    def _step_energy(self, water_metrics, food_metrics):
        """Calculo demanda y oferta de energía."""
        s = self.state
        p = self.params
        
        if 'intensity_energy_ind_current' not in s:
            s['intensity_energy_ind_current'] = p['intensity_energy_ind']
            s['intensity_energy_dom_current'] = p['intensity_energy_dom']
            
        efficiency_rate = self.scenarios.get('growth_energy_efficiency', 0.015)
        s['intensity_energy_ind_current'] *= (1 - efficiency_rate)
        s['intensity_energy_dom_current'] *= (1 - efficiency_rate)
        
        ed_ind = s['gdp'] * s['intensity_energy_ind_current']
        ed_dom = s['population'] * s['intensity_energy_dom_current']
        ed_water = water_metrics['water_demand'] * p['energy_per_m3_water']
        ed_agri = food_metrics['food_supply_total'] * p.get('energy_intensity_agri', 0)
        
        total_ed = ed_ind + ed_dom + ed_water + ed_agri

        # Modelo calibrado con crecimiento por tramos:
        # 2005-2013: +0.23% anual (estabilidad)
        # 2014-2020: -7.16% anual (reforma energética)
        transition_year = self.scenarios.get('energy_transition_year', 2013)
        
        if s['year'] <= transition_year:
            growth_rate = self.scenarios.get('growth_energy_supply', 0.0023)
        else:
            growth_rate = self.scenarios.get('growth_energy_supply_post_2013', -0.0716)
        
        s['energy_production_total'] *= (1 + growth_rate)
        
        bioenergy = food_metrics['production_grains'] * p.get('straw_energy_factor', 0)
        supply_renewables = s['es_renewables'] + bioenergy
        
        total_es = s['energy_production_total']
        
        base_coal = self.state.get('es_coal_base', self.state.get('es_coal', 470.137))
        base_oil = self.state.get('es_oil_base', self.state.get('es_oil', 7752.316))
        base_gas = self.state.get('es_gas_base', self.state.get('es_gas', 2532.210))
        
        if 'es_coal_base' not in self.state:
            self.state['es_coal_base'] = base_coal
            self.state['es_oil_base'] = base_oil
            self.state['es_gas_base'] = base_gas
        
        total_fossil_base = base_coal + base_oil + base_gas
        
        if total_fossil_base > 0:
            ratio_coal = base_coal / total_fossil_base
            ratio_oil = base_oil / total_fossil_base
            ratio_gas = base_gas / total_fossil_base
        else:
            ratio_coal = 0.0437
            ratio_oil = 0.7208
            ratio_gas = 0.2354
        
        fossil_supply = max(0, total_es - supply_renewables)
        
        s['es_coal'] = fossil_supply * ratio_coal
        s['es_oil'] = fossil_supply * ratio_oil
        s['es_gas'] = fossil_supply * ratio_gas
        
        e_r = total_es / total_ed if total_ed > 0 else 0
        
        return {
            'energy_demand': total_ed, 
            'energy_supply': total_es, 
            'energy_ratio': e_r,
            'consumption_coal': s['es_coal'], 
            'consumption_oil': s['es_oil'],
            'consumption_gas': s['es_gas'],
            'supply_renewables': supply_renewables,
            'ratio_coal': ratio_coal,
            'ratio_oil': ratio_oil,
            'ratio_gas': ratio_gas
        }

    def _step_ecology(self, energy_metrics):
        """Calculo emisiones de CO2 y COD."""
        s = self.state
        p = self.params
        
        # Calculo emisiones basadas en DEMANDA, no en producción nacional
        # (incluye importaciones virtuales)
        total_energy_needed = energy_metrics['energy_demand']
        renewables = energy_metrics.get('supply_renewables', 0)
        
        fossil_energy_burned = max(0, total_energy_needed - renewables)
        
        ratio_coal = energy_metrics.get('ratio_coal', 0.044)
        ratio_oil = energy_metrics.get('ratio_oil', 0.721)
        ratio_gas = energy_metrics.get('ratio_gas', 0.235)
        
        burn_coal = fossil_energy_burned * ratio_coal
        burn_oil = fossil_energy_burned * ratio_oil
        burn_gas = fossil_energy_burned * ratio_gas
        
        co2_coal = burn_coal * p['emission_factor_coal']
        co2_oil = burn_oil * p['emission_factor_oil']
        co2_gas = burn_gas * p.get('emission_factor_gas', 0)
        
        total_co2_energy = (co2_coal + co2_oil + co2_gas) / 1000000.0
        
        if 'co2_non_energy_current' not in s:
            s['co2_non_energy_current'] = p.get('co2_non_energy', 0)
        
        transition_year = self.scenarios.get('energy_transition_year', 2013)
        
        if s['year'] <= transition_year:
            growth_rate_non_energy = p.get('growth_co2_non_energy', 0.0128)
        else:
            growth_rate_non_energy = p.get('growth_co2_non_energy_post_2013', -0.0192)
        
        s['co2_non_energy_current'] *= (1 + growth_rate_non_energy)
        
        total_co2 = total_co2_energy + s['co2_non_energy_current']
        
        wastewater = (s['population'] * p['quota_water_dom']) * 0.8
        total_cod = wastewater * p['pollutant_concentration_dom']
        
        return {'total_co2': total_co2, 'total_cod': total_cod}

    def run(self, years=10):
        """Ejecuto la simulación principal."""
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
            
            # Simulo estrés hídrico regional: si water_ratio < 3.0, hay sobreexplotación
            if water_res['water_ratio'] < 3.0:
                factor_regional = 0.005
                extraccion_insostenible = water_res['water_demand'] * factor_regional
                self.state['ws_ground'] -= extraccion_insostenible
                
                if self.state['ws_ground'] < 0:
                    self.state['ws_ground'] = 0
            
            self.current_year += 1
            self.state['year'] = self.current_year
            
        return pd.DataFrame(self.history)

    def calibrar(self, datos_reales_df):
        """Comparo simulación vs realidad (Validación histórica)."""
        years_to_sim = len(datos_reales_df)
        simulacion = self.run(years=years_to_sim)
        
        errores = {}
        print("\n--- REPORTE DE CALIBRACIÓN (Simulación vs. Base de Datos) ---")
        
        mapa_vars = {
            'water_demand':      'demanda_agua_total',
            'total_co2':         'emisiones_co2_real',
            'food_supply_total': ['prod_granos_real', 'prod_hortalizas_real', 'prod_frutas_real', 'prod_carne_real', 'prod_lacteos_real'],
            'energy_demand':     'consumo_energia_real',
            'energy_supply':     'oferta_energia_real'
        }
        
        for var_sim, var_db in mapa_vars.items():
            val_sim = simulacion[var_sim].values
            
            if isinstance(var_db, list):
                val_real = datos_reales_df[var_db].sum(axis=1).values
            else:
                val_real = datos_reales_df[var_db].values
            
            val_real_safe = val_real.copy()
            val_real_safe[val_real_safe == 0] = 1 
            
            error = abs((val_sim - val_real) / val_real_safe).mean() * 100
            errores[var_sim] = error
            
            estado = "✅ OK" if error <= 5.0 else "⚠️ AJUSTAR"
            print(f"Variable: {var_sim:<20} | Error Promedio: {error:.2f}% -> {estado}")
        
        return errores
import pandas as pd
import numpy as np
import json
from wefe_model import WEFEModel
from tabla_validacion_completa import get_real_data

def objective_function(params, real_co2, years):
    # Update config with new params
    with open('config_mexico_2005.json', 'r') as f:
        config = json.load(f)
    
    config['params']['emission_factor_coal'] = params[0]
    config['params']['emission_factor_oil'] = params[1]
    config['params']['emission_factor_gas'] = params[2]
    
    model = WEFEModel(
        initial_data=config['initial_data'],
        params=config['params'],
        scenarios=config['scenarios']
    )
    
    sim_df = model.run(years=len(years))
    sim_co2 = sim_df['total_co2'].values
    
    # Calculate MAPE
    # Avoid division by zero
    real_safe = real_co2.copy()
    real_safe[real_safe == 0] = 1
    
    mape = np.mean(np.abs((sim_co2 - real_co2) / real_safe)) * 100
    return mape

def calibrate():
    print("Loading real data...")
    real_df = get_real_data()
    real_co2 = real_df['emisiones_co2_real'].values
    years = real_df['anio'].values
    
    # Initial guess (Current values)
    # Coal: 85000, Oil: 74000, Gas: 37000
    # We know we need to reduce them significantly (approx 0.6x)
    initial_guess = [50000, 45000, 25000]
    
    print(f"Starting calibration with initial guess: {initial_guess}")
    
    # Simple Grid Search or Random Search because I can't import scipy.optimize easily
    best_mape = float('inf')
    best_params = initial_guess
    
    # Ranges
    coal_range = [30000, 40000, 50000, 60000, 70000]
    oil_range = [30000, 40000, 50000, 60000]
    gas_range = [20000, 30000, 40000, 50000]
    
    for c in coal_range:
        for o in oil_range:
            for g in gas_range:
                mape = objective_function([c, o, g], real_co2, years)
                if mape < best_mape:
                    best_mape = mape
                    best_params = [c, o, g]
                    print(f"New Best: {mape:.2f}% -> Coal: {c}, Oil: {o}, Gas: {g}")
    
    print("\n--- CALIBRATION RESULTS ---")
    print(f"Best MAPE: {best_mape:.2f}%")
    print(f"Best Params: Coal={best_params[0]}, Oil={best_params[1]}, Gas={best_params[2]}")

if __name__ == "__main__":
    calibrate()

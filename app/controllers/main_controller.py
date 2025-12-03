from flask import Blueprint, render_template, request, jsonify, send_file
import json
import pandas as pd
import io
from app.models.wefe_model import WEFEModel

main_bp = Blueprint('main', __name__)

CONFIG_FILE = 'config_mexico_2005.json'

def load_config():
    """Carga la configuración desde el archivo JSON"""
    with open(CONFIG_FILE, 'r') as f:
        return json.load(f)

@main_bp.route('/')
def index():
    """Sirve la página principal"""
    return render_template('index.html')

@main_bp.route('/api/config', methods=['GET'])
def get_config():
    """Obtiene la configuración actual del modelo"""
    try:
        config = load_config()
        return jsonify({
            'success': True,
            'config': config
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@main_bp.route('/api/simulate', methods=['POST'])
def simulate():
    """Ejecuta una simulación con los parámetros proporcionados"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'No se recibieron datos'
            }), 400
        
        initial_data = data.get('initial_data', {})
        params = data.get('params', {})
        scenarios = data.get('scenarios', {})
        years = data.get('years', 30)
        
        if not isinstance(years, int) or years < 1 or years > 100:
            return jsonify({
                'success': False,
                'error': 'El número de años debe ser un entero entre 1 y 100'
            }), 400
        
        modelo = WEFEModel(
            initial_data=initial_data,
            params=params,
            scenarios=scenarios
        )
        
        resultados = modelo.run(years=years)
        resultados_json = resultados.to_dict(orient='records')
        
        summary = {
            'total_years': len(resultados),
            'start_year': int(resultados['year'].iloc[0]),
            'end_year': int(resultados['year'].iloc[-1]),
            'final_water_ratio': float(resultados['water_ratio'].iloc[-1]),
            'final_food_ratio': float(resultados['food_ratio'].iloc[-1]),
            'final_energy_ratio': float(resultados['energy_ratio'].iloc[-1]),
            'final_energy_demand': float(resultados['energy_demand'].iloc[-1]),
            'final_energy_supply': float(resultados['energy_supply'].iloc[-1]),
            'total_co2_emissions': float(resultados['total_co2'].sum()),
            'avg_water_stress': float(resultados['water_ratio'].mean())
        }
        
        return jsonify({
            'success': True,
            'results': resultados_json,
            'summary': summary
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@main_bp.route('/api/export/csv', methods=['POST'])
def export_csv():
    """Exporta los resultados de la simulación a CSV"""
    try:
        data = request.get_json()
        results = data.get('results', [])
        
        if not results:
            return jsonify({
                'success': False,
                'error': 'No hay resultados para exportar'
            }), 400
        
        df = pd.DataFrame(results)
        
        output = io.StringIO()
        df.to_csv(output, index=False)
        output.seek(0)
        
        output_bytes = io.BytesIO()
        output_bytes.write(output.getvalue().encode('utf-8'))
        output_bytes.seek(0)
        
        return send_file(
            output_bytes,
            mimetype='text/csv',
            as_attachment=True,
            download_name='simulacion_wefe.csv'
        )
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@main_bp.route('/api/scenarios', methods=['GET'])
def get_scenarios():
    """Obtiene escenarios predefinidos para la simulación WEFE"""
    scenarios = {
        'base_2005': {
            'name': 'Caso Base 2005 (Business as Usual)',
            'description': 'Configuración histórica de México 2005 con tasas de crecimiento moderadas',
            'scenarios': {
                'growth_pop': 0.0115,
                'growth_gdp': 0.01,
                'growth_urbanization': 0.0176,
                'growth_agri_yield': 0.022
            }
        },
        'crecimiento_acelerado': {
            'name': 'Crecimiento Acelerado (Presión WEFE)',
            'description': 'Alto crecimiento poblacional y económico - máxima presión sobre recursos agua-energía-alimento',
            'scenarios': {
                'growth_pop': 0.020,
                'growth_gdp': 0.045,
                'growth_urbanization': 0.008,
                'growth_agri_yield': 0.015
            }
        },
        'transicion_sostenible': {
            'name': 'Transición Sostenible (Eficiencia WEFE)',
            'description': 'Crecimiento controlado con innovación tecnológica - eficiencia en uso de recursos',
            'scenarios': {
                'growth_pop': 0.008,
                'growth_gdp': 0.032,
                'growth_urbanization': 0.005,
                'growth_agri_yield': 0.040
            }
        }
    }
    
    return jsonify({
        'success': True,
        'scenarios': scenarios
    })

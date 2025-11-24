from flask import Flask, render_template, request, jsonify, send_file
from flask_cors import CORS
import json
import pandas as pd
from wefe_model import WEFEModel
import io
import csv

app = Flask(__name__)
CORS(app)

# Ruta al archivo de configuración
CONFIG_FILE = 'config_mexico_2005.json'

def load_config():
    """Carga la configuración desde el archivo JSON"""
    with open(CONFIG_FILE, 'r') as f:
        return json.load(f)

@app.route('/')
def index():
    """Sirve la página principal"""
    return render_template('index.html')

@app.route('/api/config', methods=['GET'])
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

@app.route('/api/simulate', methods=['POST'])
def simulate():
    """
    Ejecuta una simulación con los parámetros proporcionados
    
    Espera un JSON con:
    - initial_data: Datos iniciales del modelo
    - params: Parámetros técnicos
    - scenarios: Escenarios de crecimiento
    - years: Número de años a simular (opcional, default: 30)
    """
    try:
        data = request.get_json()
        
        # Validar que se recibieron los datos necesarios
        if not data:
            return jsonify({
                'success': False,
                'error': 'No se recibieron datos'
            }), 400
        
        # Extraer parámetros
        initial_data = data.get('initial_data', {})
        params = data.get('params', {})
        scenarios = data.get('scenarios', {})
        years = data.get('years', 30)
        
        # Validar años
        if not isinstance(years, int) or years < 1 or years > 100:
            return jsonify({
                'success': False,
                'error': 'El número de años debe ser un entero entre 1 y 100'
            }), 400
        
        # Crear y ejecutar el modelo
        modelo = WEFEModel(
            initial_data=initial_data,
            params=params,
            scenarios=scenarios
        )
        
        resultados = modelo.run(years=years)
        
        # Convertir DataFrame a formato JSON amigable
        resultados_json = resultados.to_dict(orient='records')
        
        # Calcular estadísticas resumidas
        summary = {
            'total_years': len(resultados),
            'start_year': int(resultados['year'].iloc[0]),
            'end_year': int(resultados['year'].iloc[-1]),
            'final_water_ratio': float(resultados['water_ratio'].iloc[-1]),
            'final_food_ratio': float(resultados['food_ratio'].iloc[-1]),
            'final_energy_ratio': float(resultados['energy_ratio'].iloc[-1]),
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

@app.route('/api/export/csv', methods=['POST'])
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
        
        # Convertir a DataFrame
        df = pd.DataFrame(results)
        
        # Crear CSV en memoria
        output = io.StringIO()
        df.to_csv(output, index=False)
        output.seek(0)
        
        # Convertir a bytes
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

@app.route('/api/scenarios', methods=['GET'])
def get_scenarios():
    """Obtiene escenarios predefinidos para la simulación WEFE"""
    scenarios = {
        'base_2005': {
            'name': 'Caso Base 2005 (Business as Usual)',
            'description': 'Configuración histórica de México 2005 con tasas de crecimiento moderadas',
            'scenarios': {
                'growth_pop': 0.0115,      # 1.15% anual - tasa histórica
                'growth_gdp': 0.01,       # 1% anual - crecimiento moderado
                'growth_urbanization': 0.0176,  # 1.76% anual
                'growth_agri_yield': 0.022     # 2.2% anual - mejora gradual
            }
        },
        'crecimiento_acelerado': {
            'name': 'Crecimiento Acelerado (Presión WEFE)',
            'description': 'Alto crecimiento poblacional y económico - máxima presión sobre recursos agua-energía-alimento',
            'scenarios': {
                'growth_pop': 0.020,       # 2.0% anual - presión demográfica alta
                'growth_gdp': 0.045,       # 4.5% anual - industrialización acelerada
                'growth_urbanization': 0.008,  # 0.8% anual - urbanización rápida
                'growth_agri_yield': 0.015     # 1.5% anual - tecnología agrícola rezagada
            }
        },
        'transicion_sostenible': {
            'name': 'Transición Sostenible (Eficiencia WEFE)',
            'description': 'Crecimiento controlado con innovación tecnológica - eficiencia en uso de recursos',
            'scenarios': {
                'growth_pop': 0.008,       # 0.8% anual - control demográfico
                'growth_gdp': 0.032,       # 3.2% anual - crecimiento verde
                'growth_urbanization': 0.005,  # 0.5% anual - urbanización planificada
                'growth_agri_yield': 0.040     # 4.0% anual - revolución agrotecnológica
            }
        }
    }
    
    return jsonify({
        'success': True,
        'scenarios': scenarios
    })

if __name__ == '__main__':
    print("🚀 Iniciando servidor WEFE...")
    print("📊 Interfaz disponible en: http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)

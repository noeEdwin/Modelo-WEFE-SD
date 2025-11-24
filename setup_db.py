
import psycopg2
from config import DB_CONFIG
import os

def execute_sql_file(filename):
    try:
        print(f"Leyendo archivo {filename}...")
        with open(filename, 'r') as f:
            sql_content = f.read()
            
        print(f"Conectando a la base de datos...")
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        
        print(f"Ejecutando SQL...")
        cur.execute(sql_content)
        conn.commit()
        
        print(f"✅ Ejecución exitosa de {filename}")
        cur.close()
        conn.close()
        return True
    except Exception as e:
        print(f"❌ Error ejecutando {filename}: {e}")
        return False

if __name__ == "__main__":
    # 1. Crear la tabla
    if execute_sql_file('modelo_wefe_ddl'):
        # 2. Poblar la tabla
        execute_sql_file('populate_validation_table.sql')

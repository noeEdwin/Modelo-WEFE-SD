import os

DB_CONFIG = {
    "dbname": os.environ.get("DB_NAME", "ModeloWEFE"),
    "user": os.environ.get("DB_USER", "postgres"),
    "password": os.environ.get("DB_PASSWORD", "9474609"),
    "host": os.environ.get("DB_HOST", "localhost"),
    "port": int(os.environ.get("DB_PORT", 5432)),
    "options": os.environ.get("DB_OPTIONS", "-c search_path=ModeloWEFE,modelo_wefe"),
}

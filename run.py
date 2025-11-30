from app import create_app

app = create_app()

if __name__ == '__main__':
    print("🚀 Iniciando servidor WEFE (MVC)...")
    print("📊 Interfaz disponible en: http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)

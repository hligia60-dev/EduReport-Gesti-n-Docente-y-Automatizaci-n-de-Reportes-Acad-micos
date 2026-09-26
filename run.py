import os
from app import create_app

# Crear la aplicación Flask mediante la fábrica
app = create_app(os.environ.get('FLASK_ENV', 'development'))

if __name__ == '__main__':
    # Ejecución del servidor local de desarrollo (escucha en 127.0.0.1 y localhost)
    app.run(host='0.0.0.0', port=5000, debug=True)

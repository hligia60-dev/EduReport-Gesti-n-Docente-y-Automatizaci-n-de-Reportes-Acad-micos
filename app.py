"""
Punto de entrada WSGI para servidores de producción.
Render / Gunicorn usa: gunicorn app:app
"""
import os
from app import create_app

# Instancia de aplicación WSGI para Gunicorn / Render
app = create_app(os.environ.get('FLASK_ENV', 'production'))

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)

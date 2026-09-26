import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import config_by_name

# Instancia global de SQLAlchemy
db = SQLAlchemy()

def create_app(config_name=None):
    """
    Fábrica de aplicaciones Flask (Application Factory Pattern).
    Crea, configura y ensambla la aplicación según el entorno.
    """
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')

    app = Flask(__name__)
    app.config.from_object(config_by_name.get(config_name, config_by_name['default']))

    # Asegurar la existencia de las carpetas de datos y reportes
    os.makedirs(app.config.get('DATABASE_DIR', 'database'), exist_ok=True)
    os.makedirs(app.config.get('REPORTS_DIR', os.path.join('reports', 'generated')), exist_ok=True)
    os.makedirs(app.config.get('IMPORTS_DIR', 'imports'), exist_ok=True)

    # Inicializar la base de datos con la app
    db.init_app(app)

    # Registro de Blueprints
    from app.routes.main_routes import main_bp
    app.register_blueprint(main_bp)

    return app

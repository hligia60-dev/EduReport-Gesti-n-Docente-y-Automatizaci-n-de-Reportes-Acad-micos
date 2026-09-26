import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    """Configuración base común para todos los entornos."""
    SECRET_KEY = os.environ.get('SECRET_KEY', 'edureport-clave-secreta-academica-2026')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Directorios del sistema
    DATABASE_DIR = os.path.join(BASE_DIR, 'database')
    REPORTS_DIR = os.path.join(BASE_DIR, 'reports', 'generated')
    IMPORTS_DIR = os.path.join(BASE_DIR, 'imports')
    
    # Base de datos SQLite por defecto
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL',
        f"sqlite:///{os.path.join(DATABASE_DIR, 'edureport.db')}"
    )

class DevelopmentConfig(Config):
    """Configuración para desarrollo local."""
    DEBUG = True

class TestingConfig(Config):
    """Configuración para pruebas unitarias."""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'

class ProductionConfig(Config):
    """Configuración para producción."""
    DEBUG = False

# Mapeo de entornos
config_by_name = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}

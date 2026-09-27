import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    """Configuración base común para todos los entornos."""
    SECRET_KEY = os.environ.get('SECRET_KEY', 'edureport-clave-secreta-academica-2026')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Opciones de conexión robustas para SQLAlchemy (evita errores de conexión caída en Render)
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 280,
    }

    # Directorios del sistema
    DATABASE_DIR = os.path.join(BASE_DIR, 'database')
    REPORTS_DIR  = os.path.join(BASE_DIR, 'reports', 'generated')
    IMPORTS_DIR  = os.path.join(BASE_DIR, 'imports')

    # Base de datos: usa DATABASE_URL de Render si está definida, o SQLite local
    _raw_db_url = os.environ.get('DATABASE_URL', '')
    if _raw_db_url.startswith('postgres://'):
        _raw_db_url = _raw_db_url.replace('postgres://', 'postgresql://', 1)

    SQLALCHEMY_DATABASE_URI = (
        _raw_db_url
        if _raw_db_url
        else f"sqlite:///{os.path.join(DATABASE_DIR, 'edureport.db')}"
    )


class DevelopmentConfig(Config):
    """Configuración para desarrollo local."""
    DEBUG = True


class TestingConfig(Config):
    """Configuración para pruebas unitarias."""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'


class ProductionConfig(Config):
    """Configuración para producción (Render)."""
    DEBUG = False
    SESSION_COOKIE_SECURE   = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'


# Mapeo de entornos
config_by_name = {
    'development': DevelopmentConfig,
    'testing':     TestingConfig,
    'production':  ProductionConfig,
    'default':     DevelopmentConfig,
}

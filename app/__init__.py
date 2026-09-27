import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import config_by_name

db = SQLAlchemy()

def create_app(config_name=None):
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')

    flask_app = Flask(__name__)
    flask_app.config.from_object(config_by_name.get(config_name, config_by_name['default']))

    os.makedirs(flask_app.config.get('DATABASE_DIR', 'database'), exist_ok=True)
    os.makedirs(flask_app.config.get('REPORTS_DIR', os.path.join('reports', 'generated')), exist_ok=True)
    os.makedirs(flask_app.config.get('IMPORTS_DIR', 'imports'), exist_ok=True)

    db.init_app(flask_app)

    from app.routes.main_routes       import main_bp
    from app.routes.student_routes    import student_bp
    from app.routes.attendance_routes import attendance_bp
    from app.routes.report_routes     import report_bp
    from app.routes.evaluation_routes import evaluation_bp
    from app.routes.seguimiento_routes import seguimiento_bp

    flask_app.register_blueprint(main_bp)
    flask_app.register_blueprint(student_bp)
    flask_app.register_blueprint(attendance_bp)
    flask_app.register_blueprint(report_bp)
    flask_app.register_blueprint(evaluation_bp)
    flask_app.register_blueprint(seguimiento_bp)

    with flask_app.app_context():
        from app import models
        db.create_all()
        from app.services.seed_service import seed_database_if_empty
        seed_database_if_empty()

    return flask_app


_app_instance = None

def __getattr__(name):
    """Permite resolver 'from app import app' o 'gunicorn app:app' automáticamente."""
    if name == 'app':
        global _app_instance
        if _app_instance is None:
            _app_instance = create_app(os.environ.get('FLASK_ENV', 'production'))
        return _app_instance
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")


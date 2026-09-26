import os
import sys
from flask import Blueprint, render_template, jsonify, send_from_directory, current_app

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """Ruta principal: Landing page interactiva y presentación del sistema."""
    context = {
        'app_name': 'EduReport',
        'subtitle': 'Sistema de Gestión Docente y Generación Automática de Reportes Académicos',
        'system_status': 'Operativo',
        'python_version': sys.version.split()[0],
        'flask_version': '3.0.3',
        'cycle_1_name': 'Primer Ciclo del Nivel Secundario',
        'cycle_1_grades': '1.º, 2.º y 3.º de Secundaria',
        'cycle_2_name': 'Segundo Ciclo del Nivel Secundario',
        'cycle_2_grades': '4.º, 5.º y 6.º de Secundaria',
        'rule_description': 'Al acumular 3 ausencias, el sistema genera automáticamente una alerta y permite emitir el informe de seguimiento de asistencia.'
    }
    return render_template('index.html', **context)

@main_bp.route('/arquitectura')
def arquitectura():
    """Página de consulta de la arquitectura técnica del sistema."""
    return render_template('arquitectura.html')

@main_bp.route('/docs/images/<path:filename>')
def serve_docs_image(filename):
    """Permite servir la imagen de arquitectura desde la carpeta docs/images."""
    docs_images_dir = os.path.abspath(os.path.join(current_app.root_path, '..', 'docs', 'images'))
    return send_from_directory(docs_images_dir, filename)

@main_bp.route('/api/status')
def api_status():
    """Endpoint JSON de salud y diagnóstico del sistema."""
    return jsonify({
        'status': 'OK',
        'application': 'EduReport',
        'environment': current_app.config.get('ENV', 'development'),
        'python_version': sys.version.split()[0],
        'cycles_supported': ['Primer Ciclo (1.º, 2.º, 3.º)', 'Segundo Ciclo (4.º, 5.º, 6.º)'],
        'rule_3_absences': 'Active'
    })

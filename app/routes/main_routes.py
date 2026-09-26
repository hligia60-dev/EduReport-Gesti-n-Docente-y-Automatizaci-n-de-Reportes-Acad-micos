import os
import sys
from flask import Blueprint, render_template, jsonify, send_from_directory, current_app
from app.models import (
    CentroEducativo,
    Aula,
    Estudiante,
    Familiar,
    Asistencia,
    Asignatura,
    CompetenciaFundamental,
    CompetenciaEspecifica,
    IndicadorLogro,
    ContenidoCurricular,
    Evaluacion,
    Seguimiento,
    Reporte,
    Student,
    Section,
    GradeLevel,
    Cycle
)
from app.services import attendance_service, student_service

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """Ruta principal: Landing page interactiva y presentación del sistema."""
    total_students = Student.query.count()
    total_sections = Section.query.count()
    alerts = attendance_service.get_students_with_alerts()

    context = {
        'app_name': 'EduReport',
        'subtitle': 'Sistema de Gestión Docente y Generación Automática de Reportes Académicos',
        'system_status': 'Operativo',
        'python_version': sys.version.split()[0],
        'flask_version': '3.0.3',
        'total_students': total_students,
        'total_sections': total_sections,
        'total_alerts': len(alerts),
        'cycle_1_name': 'Primer Ciclo del Nivel Secundario',
        'cycle_1_grades': '1.º, 2.º y 3.º de Secundaria',
        'cycle_2_name': 'Segundo Ciclo del Nivel Secundario',
        'cycle_2_grades': '4.º, 5.º y 6.º de Secundaria',
        'rule_description': 'Al acumular 3 ausencias, el sistema genera automáticamente una alerta preventiva y permite emitir el informe de seguimiento de asistencia.'
    }
    return render_template('index.html', **context)

@main_bp.route('/dashboard')
def dashboard():
    """Panel de control principal con graficos interactivos de asistencia y rendimiento."""
    from app.models.evaluation import Seguimiento, Reporte
    from app.services.evaluation_service import get_academic_global_stats

    total_students  = Student.query.count()
    total_sections  = Section.query.count()
    alerts          = attendance_service.get_students_with_alerts()
    att_stats       = attendance_service.get_attendance_stats()
    acad_stats      = get_academic_global_stats()
    total_segs      = Seguimiento.query.count()
    segs_abiertos   = Seguimiento.query.filter_by(status='Abierto').count()
    total_reportes  = Reporte.query.count()

    cycles = Cycle.query.all()
    cycle_chart_labels   = [c.name for c in cycles]
    cycle_chart_students = [sum(len(s.students) for g in c.grades for s in g.sections) for c in cycles]
    cycle_chart_alerts   = [att_stats['c1_alerts'], att_stats['c2_alerts']]

    return render_template(
        'dashboard.html',
        total_students=total_students,
        total_sections=total_sections,
        total_alerts=len(alerts),
        alerts=alerts,
        att_stats=att_stats,
        acad_stats=acad_stats,
        total_segs=total_segs,
        segs_abiertos=segs_abiertos,
        total_reportes=total_reportes,
        cycle_labels=cycle_chart_labels,
        cycle_students=cycle_chart_students,
        cycle_alerts=cycle_chart_alerts,
    )

@main_bp.route('/entorno')
def entorno():
    """Visualizador técnico del entorno de ejecución, base de datos y configuración."""
    db_path = current_app.config.get('SQLALCHEMY_DATABASE_URI', '').replace('sqlite:///', '')
    db_exists = os.path.exists(db_path)
    db_size = os.path.getsize(db_path) if db_exists else 0

    tables_info = [
        {'name': 'CentroEducativo (centros_educativos)', 'count': CentroEducativo.query.count()},
        {'name': 'Aula (aulas)', 'count': Aula.query.count()},
        {'name': 'Estudiante (estudiantes)', 'count': Estudiante.query.count()},
        {'name': 'Familiar (familiares)', 'count': Familiar.query.count()},
        {'name': 'Asistencia (asistencias)', 'count': Asistencia.query.count()},
        {'name': 'Asignatura (asignaturas)', 'count': Asignatura.query.count()},
        {'name': 'CompetenciaFundamental (competencias_fundamentales)', 'count': CompetenciaFundamental.query.count()},
        {'name': 'CompetenciaEspecifica (competencias_especificas)', 'count': CompetenciaEspecifica.query.count()},
        {'name': 'IndicadorLogro (indicadores_logro)', 'count': IndicadorLogro.query.count()},
        {'name': 'ContenidoCurricular (contenidos_curriculares)', 'count': ContenidoCurricular.query.count()},
        {'name': 'Evaluacion (evaluaciones)', 'count': Evaluacion.query.count()},
        {'name': 'Seguimiento (seguimientos)', 'count': Seguimiento.query.count()},
        {'name': 'Reporte (reportes)', 'count': Reporte.query.count()},
        {'name': 'Cycle (cycles)', 'count': Cycle.query.count()},
        {'name': 'GradeLevel (grade_levels)', 'count': GradeLevel.query.count()},
    ]

    routes_info = []
    for rule in current_app.url_map.iter_rules():
        if not rule.rule.startswith('/static'):
            routes_info.append({
                'endpoint': rule.endpoint,
                'methods': ', '.join(m for m in rule.methods if m not in ('HEAD', 'OPTIONS')),
                'rule': rule.rule
            })
    routes_info.sort(key=lambda r: r['rule'])

    env_data = {
        'python_version': sys.version,
        'python_executable': sys.executable,
        'is_venv': sys.prefix != sys.base_prefix,
        'venv_prefix': sys.prefix,
        'flask_env': current_app.config.get('ENV', 'development'),
        'debug_mode': current_app.debug,
        'db_path': db_path,
        'db_size_kb': round(db_size / 1024, 2),
        'tables_info': tables_info,
        'routes_info': routes_info
    }

    return render_template('environment.html', env=env_data)

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
    alerts_count = len(attendance_service.get_students_with_alerts())
    return jsonify({
        'status': 'OK',
        'application': 'EduReport',
        'environment': current_app.config.get('ENV', 'development'),
        'python_version': sys.version.split()[0],
        'total_students': Student.query.count(),
        'total_alerts_3_absences': alerts_count,
        'cycles_supported': ['Primer Ciclo (1.º, 2.º, 3.º)', 'Segundo Ciclo (4.º, 5.º, 6.º)'],
        'rule_3_absences': 'Active'
    })

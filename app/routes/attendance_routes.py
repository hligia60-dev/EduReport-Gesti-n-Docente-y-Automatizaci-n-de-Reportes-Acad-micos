from datetime import date, datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from app.models.academic import Section, Student
from app.models.attendance import Attendance
from app.services import attendance_service, student_service

attendance_bp = Blueprint('attendance', __name__, url_prefix='/asistencia')


# ── 1. Índice del módulo de asistencia ────────────────────────────────────────
@attendance_bp.route('/')
def index():
    """Resumen del módulo de asistencia con estadísticas globales P/T/A/E."""
    stats   = attendance_service.get_attendance_stats()
    alerts  = attendance_service.get_students_with_alerts()
    sections = student_service.get_all_sections()
    return render_template(
        'attendance/index.html',
        stats=stats,
        alerts=alerts,
        sections=sections,
        badge_classes=attendance_service.BADGE_CLASSES
    )


# ── 2. Pase de lista diario por sección ──────────────────────────────────────
@attendance_bp.route('/pase-lista', methods=['GET', 'POST'])
@attendance_bp.route('/diaria', methods=['GET', 'POST'])
@attendance_bp.route('/registrar', methods=['GET', 'POST'])
def register_daily():

    """Registro de asistencia diaria por sección escolar (P/T/A/E)."""
    section_id = request.args.get('section_id', type=int)
    date_str   = request.args.get('date', date.today().isoformat())

    try:
        current_date = datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        current_date = date.today()

    sections = student_service.get_all_sections()
    selected_section = Section.query.get(section_id) if section_id else (sections[0] if sections else None)

    if request.method == 'POST':
        posted_section_id = request.form.get('section_id', type=int)
        posted_date_str   = request.form.get('date', date.today().isoformat())

        try:
            target_date = datetime.strptime(posted_date_str, '%Y-%m-%d').date()
        except ValueError:
            target_date = date.today()

        student_status_dict = {}
        notes_dict          = {}

        for key, value in request.form.items():
            if key.startswith('status_'):
                student_id = int(key.split('_')[1])
                student_status_dict[student_id] = value
            elif key.startswith('note_'):
                student_id_str = key.split('_', 1)[1]
                notes_dict[student_id_str] = value

        if student_status_dict:
            count = attendance_service.record_attendance_batch(
                student_status_dict, target_date, notes_dict
            )
            flash(
                f'✓ Asistencia guardada: {count} estudiantes registrados para el {target_date.strftime("%d/%m/%Y")}.',
                'success'
            )

        return redirect(url_for(
            'attendance.register_daily',
            section_id=posted_section_id,
            date=posted_date_str
        ))

    # Cargar datos de estudiantes con su estado actual en esa fecha
    students_data = attendance_service.get_section_attendance_for_date(
        selected_section.id if selected_section else None,
        current_date
    ) if selected_section else []

    return render_template(
        'attendance/register.html',
        sections=sections,
        selected_section=selected_section,
        selected_date=current_date.isoformat(),
        selected_date_display=current_date.strftime('%d/%m/%Y'),
        students_data=students_data,
        badge_classes=attendance_service.BADGE_CLASSES
    )


# ── 3. Historial de asistencia de un estudiante ───────────────────────────────
@attendance_bp.route('/estudiante/<int:student_id>')
def student_detail(student_id):
    """Historial completo de asistencia de un estudiante con estadísticas P/T/A/E."""
    student  = Student.query.get_or_404(student_id)
    summary  = attendance_service.get_student_attendance_summary(student_id)
    history  = attendance_service.get_student_history(student_id, limit=90)
    return render_template(
        'attendance/student_detail.html',
        student=student,
        summary=summary,
        history=history,
        badge_classes=attendance_service.BADGE_CLASSES
    )


# ── 4. Registrar asistencia individual desde la ficha del estudiante ──────────
@attendance_bp.route('/estudiante/<int:student_id>/registrar', methods=['POST'])
def register_single(student_id):
    """Registra o actualiza la asistencia de un único estudiante desde su ficha."""
    student    = Student.query.get_or_404(student_id)
    att_date_str = request.form.get('date', date.today().isoformat())
    status     = request.form.get('status', 'Presente')
    notes      = request.form.get('notes', '').strip()

    try:
        att_date = datetime.strptime(att_date_str, '%Y-%m-%d').date()
    except ValueError:
        att_date = date.today()

    attendance_service.record_single_attendance(student_id, att_date, status, notes)
    flash(
        f'Asistencia de {student.full_name} registrada como «{status}» '
        f'para el {att_date.strftime("%d/%m/%Y")}.',
        'success'
    )
    return redirect(url_for('attendance.student_detail', student_id=student_id))


# ── 5. Eliminar un registro de asistencia ────────────────────────────────────
@attendance_bp.route('/registro/<int:record_id>/eliminar', methods=['POST'])
def delete_record(record_id):
    """Elimina un registro individual de asistencia."""
    att = Attendance.query.get_or_404(record_id)
    student_id = att.student_id
    fecha_str  = att.date.strftime('%d/%m/%Y') if att.date else '?'
    db_status  = att.status
    attendance_service.delete_attendance_record(record_id)
    flash(f'Registro de asistencia ({db_status} – {fecha_str}) eliminado.', 'info')
    return redirect(url_for('attendance.student_detail', student_id=student_id))


# ── 6. Bandeja de alertas (≥3 ausencias) ─────────────────────────────────────
@attendance_bp.route('/alertas')
def alerts():
    """
    Bandeja de Alertas de Ausentismo:
    Muestra exclusivamente a los estudiantes que han acumulado 3 o más ausencias.
    Permite generar el informe de seguimiento desde aquí.
    """
    alerts_data = attendance_service.get_students_with_alerts()
    return render_template(
        'attendance/alerts.html',
        alerts=alerts_data,
        badge_classes=attendance_service.BADGE_CLASSES
    )


# ── 7. Insertar datos de prueba (demo) ───────────────────────────────────────
@attendance_bp.route('/demo/seed', methods=['POST'])
def seed_demo():
    """
    Inserta datos ficticios de asistencia para demostrar la Regla de 3 Ausencias.
    Solo disponible en modo desarrollo.
    """
    seeded = attendance_service.seed_demo_attendance()
    if seeded > 0:
        flash(
            f'✓ {seeded} registros de asistencia demo insertados. '
            'Se activaron alertas por 3+ ausencias. Revisa la bandeja de alertas.',
            'success'
        )
    else:
        flash('Los datos de demo ya estaban cargados o no hay estudiantes.', 'info')
    return redirect(url_for('attendance.alerts'))



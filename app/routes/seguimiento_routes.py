from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.models.academic import Student
from app.services import seguimiento_service, student_service, attendance_service

seguimiento_bp = Blueprint('seguimiento', __name__, url_prefix='/seguimiento')


@seguimiento_bp.route('/')
def index():
    """Lista general de seguimientos activos con estadisticas."""
    seguimientos = seguimiento_service.get_all_seguimientos()
    stats = seguimiento_service.get_seguimiento_stats()
    return render_template('seguimiento/index.html',
                           seguimientos=seguimientos, stats=stats,
                           tipos=seguimiento_service.TIPOS_SEGUIMIENTO,
                           estados=seguimiento_service.ESTADOS_SEGUIMIENTO)


@seguimiento_bp.route('/estudiante/<int:student_id>')
def ficha(student_id):
    """Ficha de seguimiento integral de un estudiante."""
    student = Student.query.get_or_404(student_id)
    seguimientos = seguimiento_service.get_seguimientos_estudiante(student_id)
    att_summary  = attendance_service.get_student_attendance_summary(student_id)
    return render_template('seguimiento/ficha.html',
                           student=student, seguimientos=seguimientos,
                           att_summary=att_summary,
                           tipos=seguimiento_service.TIPOS_SEGUIMIENTO,
                           estados=seguimiento_service.ESTADOS_SEGUIMIENTO)


@seguimiento_bp.route('/nuevo', methods=['GET', 'POST'])
def nuevo():
    """Formulario para registrar un nuevo seguimiento."""
    students = student_service.get_all_students()
    sections = student_service.get_all_sections()

    if request.method == 'POST':
        student_id = request.form.get('student_id', type=int)
        aula_id    = request.form.get('aula_id', type=int)
        fecha      = request.form.get('fecha', '').strip()
        tipo       = request.form.get('tipo', '').strip()
        motivo     = request.form.get('motivo', '').strip()
        descripcion = request.form.get('descripcion', '').strip()
        acciones   = request.form.get('acciones_acordadas', '').strip()
        status     = request.form.get('status', 'Abierto').strip()
        responsable = request.form.get('responsable', '').strip() or 'Departamento de Orientacion y Psicologia'
        fecha_res  = request.form.get('fecha_resolucion', '').strip()

        if not student_id or not tipo or not motivo:
            flash('Estudiante, tipo y motivo son campos obligatorios.', 'danger')
            return redirect(url_for('seguimiento.nuevo'))

        seg = seguimiento_service.save_seguimiento(
            student_id=student_id, aula_id=aula_id, fecha_str=fecha,
            tipo=tipo, motivo=motivo, descripcion=descripcion,
            acciones=acciones, status=status, responsable=responsable,
            fecha_resolucion_str=fecha_res
        )
        student = Student.query.get(student_id)
        flash(f'Seguimiento de {tipo} registrado para {student.full_name if student else ""}.', 'success')
        return redirect(url_for('seguimiento.ficha', student_id=student_id))

    student_id = request.args.get('student_id', type=int)
    selected_student = Student.query.get(student_id) if student_id else None

    return render_template('seguimiento/form.html',
                           students=students, sections=sections,
                           selected_student=selected_student,
                           tipos=seguimiento_service.TIPOS_SEGUIMIENTO,
                           estados=seguimiento_service.ESTADOS_SEGUIMIENTO,
                           seg=None)


@seguimiento_bp.route('/editar/<int:seg_id>', methods=['GET', 'POST'])
def editar(seg_id):
    """Formulario para editar un seguimiento existente."""
    seg = seguimiento_service.get_seguimiento(seg_id)
    students = student_service.get_all_students()
    sections = student_service.get_all_sections()

    if request.method == 'POST':
        student_id = request.form.get('student_id', type=int)
        aula_id    = request.form.get('aula_id', type=int)
        fecha      = request.form.get('fecha', '').strip()
        tipo       = request.form.get('tipo', '').strip()
        motivo     = request.form.get('motivo', '').strip()
        descripcion = request.form.get('descripcion', '').strip()
        acciones   = request.form.get('acciones_acordadas', '').strip()
        status     = request.form.get('status', 'Abierto').strip()
        responsable = request.form.get('responsable', '').strip() or 'Departamento de Orientacion y Psicologia'
        fecha_res  = request.form.get('fecha_resolucion', '').strip()

        seguimiento_service.save_seguimiento(
            student_id=student_id, aula_id=aula_id, fecha_str=fecha,
            tipo=tipo, motivo=motivo, descripcion=descripcion,
            acciones=acciones, status=status, responsable=responsable,
            fecha_resolucion_str=fecha_res, seg_id=seg_id
        )
        flash('Seguimiento actualizado correctamente.', 'success')
        return redirect(url_for('seguimiento.ficha', student_id=student_id))

    return render_template('seguimiento/form.html',
                           students=students, sections=sections,
                           selected_student=seg.estudiante,
                           tipos=seguimiento_service.TIPOS_SEGUIMIENTO,
                           estados=seguimiento_service.ESTADOS_SEGUIMIENTO,
                           seg=seg)


@seguimiento_bp.route('/eliminar/<int:seg_id>', methods=['POST'])
def eliminar(seg_id):
    seg = seguimiento_service.get_seguimiento(seg_id)
    student_id = seg.student_id
    seguimiento_service.delete_seguimiento(seg_id)
    flash('Seguimiento eliminado.', 'info')
    return redirect(url_for('seguimiento.ficha', student_id=student_id))


@seguimiento_bp.route('/demo/seed', methods=['POST'])
def seed_demo():
    count = seguimiento_service.seed_demo_seguimientos()
    flash(f'{count} seguimientos de alerta creados automaticamente desde las alertas de asistencia.', 'success')
    return redirect(url_for('seguimiento.index'))

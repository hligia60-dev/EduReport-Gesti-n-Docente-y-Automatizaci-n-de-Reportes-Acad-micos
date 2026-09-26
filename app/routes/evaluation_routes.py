from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.models.academic import Student
from app.services import evaluation_service, student_service, attendance_service

evaluation_bp = Blueprint('evaluation', __name__, url_prefix='/evaluaciones')


@evaluation_bp.route('/')
def index():
    """Resumen del modulo de evaluaciones con estadisticas globales."""
    stats = evaluation_service.get_academic_global_stats()
    sections = student_service.get_all_sections()
    asignaturas = evaluation_service.get_all_asignaturas()
    return render_template('evaluation/index.html',
                           stats=stats, sections=sections, asignaturas=asignaturas)


@evaluation_bp.route('/estudiante/<int:student_id>')
def student_grades(student_id):
    """Ficha academica completa de un estudiante con evolucion por periodo."""
    student  = Student.query.get_or_404(student_id)
    summary  = evaluation_service.get_student_academic_summary(student_id)
    asignaturas = evaluation_service.get_all_asignaturas()
    att_summary = attendance_service.get_student_attendance_summary(student_id)
    return render_template('evaluation/student_grades.html',
                           student=student, summary=summary,
                           asignaturas=asignaturas, periods=evaluation_service.PERIODS,
                           att_summary=att_summary)


@evaluation_bp.route('/registrar', methods=['GET', 'POST'])
def register():
    """Formulario de registro / edicion de calificaciones por estudiante."""
    sections    = student_service.get_all_sections()
    asignaturas = evaluation_service.get_all_asignaturas()
    students    = student_service.get_all_students()

    if request.method == 'POST':
        student_id  = request.form.get('student_id', type=int)
        asig_id     = request.form.get('asignatura_id', type=int)
        period      = request.form.get('period', '').strip()
        score_str   = request.form.get('score', '0').strip()
        rec_str     = request.form.get('calificacion_recuperacion', '').strip()
        observ      = request.form.get('observaciones', '').strip()
        eval_id     = request.form.get('eval_id', type=int)

        try:
            score = float(score_str)
        except ValueError:
            flash('La calificacion debe ser un numero entre 0 y 100.', 'danger')
            return redirect(url_for('evaluation.register'))

        rec = None
        if rec_str:
            try:
                rec = float(rec_str)
            except ValueError:
                rec = None

        ev = evaluation_service.save_evaluacion(
            student_id=student_id,
            asignatura_id=asig_id,
            period=period,
            score=score,
            calificacion_recuperacion=rec,
            observaciones=observ,
            eval_id=eval_id
        )

        student = Student.query.get(student_id)
        flash(f'Calificacion de {student.full_name if student else ""} en {period} guardada correctamente.', 'success')
        return redirect(url_for('evaluation.student_grades', student_id=student_id))

    student_id_get = request.args.get('student_id', type=int)
    selected_student = Student.query.get(student_id_get) if student_id_get else None
    eval_id = request.args.get('eval_id', type=int)
    ev_to_edit = evaluation_service.get_evaluacion(eval_id) if eval_id else None

    return render_template('evaluation/register.html',
                           sections=sections, asignaturas=asignaturas,
                           students=students, periods=evaluation_service.PERIODS,
                           selected_student=selected_student, ev_to_edit=ev_to_edit)


@evaluation_bp.route('/eliminar/<int:eval_id>', methods=['POST'])
def delete(eval_id):
    ev = evaluation_service.get_evaluacion(eval_id)
    student_id = ev.student_id
    evaluation_service.delete_evaluacion(eval_id)
    flash('Calificacion eliminada.', 'info')
    return redirect(url_for('evaluation.student_grades', student_id=student_id))


@evaluation_bp.route('/demo/seed', methods=['POST'])
def seed_demo():
    count = evaluation_service.seed_demo_evaluaciones()
    if count > 0:
        flash(f'{count} calificaciones demo insertadas. Puedes ver la evolucion academica.', 'success')
    else:
        flash('Los datos demo ya estaban cargados o no hay estudiantes/asignaturas.', 'info')
    return redirect(url_for('evaluation.index'))

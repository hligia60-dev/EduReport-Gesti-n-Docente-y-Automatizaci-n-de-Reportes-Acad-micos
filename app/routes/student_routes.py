from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.models.academic import Student, Section, GradeLevel, Cycle
from app.services import student_service

student_bp = Blueprint('students', __name__, url_prefix='/estudiantes')

@student_bp.route('/')
def list_students():
    """
    Listar y Buscar estudiantes con filtros por ciclo (Primer / Segundo Ciclo),
    grado (1.º a 6.º), sección/aula y búsqueda textual (nombre, apellido, RNE).
    """
    cycle_id = request.args.get('cycle_id', type=int)
    grade_id = request.args.get('grade_id', type=int)
    section_id = request.args.get('section_id', type=int)
    search = request.args.get('q', type=str)

    students = student_service.get_all_students(
        cycle_id=cycle_id,
        grade_id=grade_id,
        section_id=section_id,
        search=search
    )
    
    cycles = student_service.get_all_cycles()
    grades = student_service.get_all_grade_levels()
    sections = student_service.get_all_sections()

    # Métricas para las tarjetas de resumen
    total_count = len(students)
    primer_ciclo_count = sum(1 for s in students if s.section.grade_level.cycle.name == 'Primer Ciclo')
    segundo_ciclo_count = sum(1 for s in students if s.section.grade_level.cycle.name == 'Segundo Ciclo')
    alertas_count = sum(1 for s in students if s.has_absence_alert)

    return render_template(
        'students/list.html',
        students=students,
        cycles=cycles,
        grades=grades,
        sections=sections,
        selected_cycle=cycle_id,
        selected_grade=grade_id,
        selected_section=section_id,
        search_query=search or '',
        total_count=total_count,
        primer_ciclo_count=primer_ciclo_count,
        segundo_ciclo_count=segundo_ciclo_count,
        alertas_count=alertas_count
    )

@student_bp.route('/nuevo', methods=['GET', 'POST'])
def new_student():
    """
    Agregar un nuevo estudiante al sistema contemplando:
    nombre, apellido, RNE/matrícula, sexo, grado, sección, ciclo,
    condición inicial, familiar/tutor y teléfono.
    """
    if request.method == 'POST':
        first_name = request.form.get('first_name', '').strip()
        last_name = request.form.get('last_name', '').strip()
        registration_number = request.form.get('registration_number', '').strip().upper()
        section_id = request.form.get('section_id', type=int)
        gender = request.form.get('gender', 'M')
        birth_date = request.form.get('birth_date', '').strip()
        condicion_inicial = request.form.get('condicion_inicial', 'Promovido')
        numero_orden = request.form.get('numero_orden', '').strip()
        tutor_name = request.form.get('tutor_name', '').strip()
        tutor_phone = request.form.get('tutor_phone', '').strip()
        tutor_relationship = request.form.get('tutor_relationship', 'Padre/Madre/Tutor')

        # Validaciones de campos obligatorios
        if not first_name or not last_name or not registration_number or not section_id:
            flash('Por favor complete los campos obligatorios: Nombres, Apellidos, RNE y Aula/Sección.', 'danger')
            return redirect(url_for('students.new_student'))

        # Validar unicidad del RNE / matrícula
        if Student.query.filter_by(registration_number=registration_number).first():
            flash(f'El RNE o matrícula "{registration_number}" ya se encuentra registrado en el sistema.', 'warning')
            return redirect(url_for('students.new_student'))

        try:
            student = student_service.create_student(
                first_name=first_name,
                last_name=last_name,
                section_id=section_id,
                registration_number=registration_number,
                gender=gender,
                birth_date=birth_date,
                condicion_inicial=condicion_inicial,
                tutor_name=tutor_name,
                tutor_phone=tutor_phone,
                tutor_relationship=tutor_relationship,
                numero_orden=numero_orden
            )
            flash(f'¡Estudiante {student.full_name} matriculado exitosamente en {student.section.full_name}!', 'success')
            return redirect(url_for('students.detail', student_id=student.id))
        except Exception as e:
            flash(f'Error al registrar estudiante: {str(e)}', 'danger')

    sections = student_service.get_all_sections()
    return render_template('students/form.html', sections=sections, student=None, is_edit=False)

@student_bp.route('/<int:student_id>')
def detail(student_id):
    """
    Consultar ficha académica individual de un estudiante con su historial de asistencia,
    contactos familiares y estado de alertas.
    """
    student = Student.query.get_or_404(student_id)
    attendances = sorted(student.attendances, key=lambda a: a.date, reverse=True)
    return render_template('students/detail.html', student=student, attendances=attendances)

@student_bp.route('/<int:student_id>/editar', methods=['GET', 'POST'])
def edit_student(student_id):
    """
    Editar la información completa de un estudiante y su contacto familiar.
    """
    student = Student.query.get_or_404(student_id)

    if request.method == 'POST':
        first_name = request.form.get('first_name', '').strip()
        last_name = request.form.get('last_name', '').strip()
        registration_number = request.form.get('registration_number', '').strip().upper()
        section_id = request.form.get('section_id', type=int)
        gender = request.form.get('gender', 'M')
        birth_date = request.form.get('birth_date', '').strip()
        condicion_inicial = request.form.get('condicion_inicial', 'Promovido')
        numero_orden = request.form.get('numero_orden', '').strip()
        tutor_name = request.form.get('tutor_name', '').strip()
        tutor_phone = request.form.get('tutor_phone', '').strip()
        tutor_relationship = request.form.get('tutor_relationship', 'Padre/Madre/Tutor')

        if not first_name or not last_name or not registration_number or not section_id:
            flash('Por favor complete los campos obligatorios: Nombres, Apellidos, RNE y Aula.', 'danger')
            return redirect(url_for('students.edit_student', student_id=student.id))

        # Validar que el RNE no esté en uso por otro estudiante diferente
        existente = Student.query.filter_by(registration_number=registration_number).first()
        if existente and existente.id != student.id:
            flash(f'El RNE "{registration_number}" pertenece a otro estudiante ({existente.full_name}).', 'warning')
            return redirect(url_for('students.edit_student', student_id=student.id))

        try:
            student_service.update_student(
                student_id=student.id,
                first_name=first_name,
                last_name=last_name,
                section_id=section_id,
                registration_number=registration_number,
                gender=gender,
                birth_date=birth_date,
                condicion_inicial=condicion_inicial,
                tutor_name=tutor_name,
                tutor_phone=tutor_phone,
                tutor_relationship=tutor_relationship,
                numero_orden=numero_orden
            )
            flash(f'¡Datos de {student.full_name} actualizados correctamente!', 'success')
            return redirect(url_for('students.detail', student_id=student.id))
        except Exception as e:
            flash(f'Error al actualizar estudiante: {str(e)}', 'danger')

    sections = student_service.get_all_sections()
    return render_template('students/form.html', sections=sections, student=student, is_edit=True)

@student_bp.route('/<int:student_id>/editar-telefono', methods=['POST'])
def edit_student_phone(student_id):
    """
    Actualización rápida del número de teléfono del estudiante y sus familiares.
    Permite presionar 'Aceptar cambio' para guardar inmediatamente.
    """
    new_phone = request.form.get('tutor_phone', '').strip()
    try:
        student = student_service.update_student_phone(student_id, new_phone)
        flash(f'¡Teléfono de {student.full_name} actualizado a "{new_phone or "(Sin teléfono)"}" exitosamente!', 'success')
    except Exception as e:
        flash(f'Error al actualizar el teléfono: {str(e)}', 'danger')

    next_url = request.form.get('next') or url_for('students.detail', student_id=student_id)
    return redirect(next_url)

@student_bp.route('/<int:student_id>/eliminar', methods=['POST'])
def delete_student(student_id):
    """
    Eliminar un estudiante del sistema.
    """
    try:
        deleted_name = student_service.delete_student(student_id)
        flash(f'El estudiante "{deleted_name}" ha sido eliminado exitosamente del sistema.', 'success')
    except Exception as e:
        flash(f'Error al eliminar el estudiante: {str(e)}', 'danger')

    return redirect(url_for('students.list_students'))

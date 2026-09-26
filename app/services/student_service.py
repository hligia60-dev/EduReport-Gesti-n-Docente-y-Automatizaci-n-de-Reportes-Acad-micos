from app import db
from app.models.academic import Student, Section, GradeLevel, Cycle, Familiar

def get_all_students(cycle_id=None, grade_id=None, section_id=None, search=None):
    """
    Obtiene el listado de estudiantes aplicando filtros opcionales de ciclo, grado, sección y búsqueda de texto.
    """
    query = Student.query.join(Section).join(GradeLevel).join(Cycle)

    if cycle_id:
        query = query.filter(Cycle.id == cycle_id)
    if grade_id:
        query = query.filter(GradeLevel.id == grade_id)
    if section_id:
        query = query.filter(Section.id == section_id)
    if search:
        search_term = f"%{search.strip()}%"
        query = query.filter(
            (Student.first_name.ilike(search_term)) |
            (Student.last_name.ilike(search_term)) |
            (Student.registration_number.ilike(search_term))
        )

    return query.order_by(GradeLevel.order, Section.name, Student.numero_orden, Student.last_name).all()

def get_student_by_id(student_id):
    """Obtiene un estudiante por su ID primario o retorna 404."""
    return Student.query.get_or_404(student_id)

def create_student(
    first_name,
    last_name,
    section_id,
    registration_number,
    gender='M',
    birth_date=None,
    condicion_inicial='Promovido',
    tutor_name=None,
    tutor_phone=None,
    tutor_relationship='Padre/Madre/Tutor',
    numero_orden=None
):
    """
    Registra un nuevo estudiante en el sistema y crea su contacto familiar asociado.
    """
    student = Student(
        first_name=first_name.strip(),
        last_name=last_name.strip(),
        section_id=section_id,
        registration_number=registration_number.strip().upper(),
        gender=gender,
        birth_date=birth_date.strip() if birth_date else None,
        condicion_inicial=condicion_inicial,
        numero_orden=int(numero_orden) if numero_orden and str(numero_orden).isdigit() else None,
        tutor_name=tutor_name.strip() if tutor_name else None,
        tutor_phone=tutor_phone.strip() if tutor_phone else None,
        tutor_relationship=tutor_relationship,
        is_active=True
    )
    db.session.add(student)
    db.session.flush()

    # Si se especificó tutor, crear o actualizar el registro en la tabla Familiares
    if tutor_name or tutor_phone:
        familiar = Familiar(
            estudiante_id=student.id,
            nombres=tutor_name.strip() if tutor_name else f"Tutor de {student.full_name}",
            parentesco=tutor_relationship,
            telefono=tutor_phone.strip() if tutor_phone else None,
            whatsapp=tutor_phone.strip() if tutor_phone else None,
            es_contacto_principal=True,
            es_contacto_emergencia=True
        )
        db.session.add(familiar)

    db.session.commit()
    return student

def update_student(
    student_id,
    first_name,
    last_name,
    section_id,
    registration_number,
    gender='M',
    birth_date=None,
    condicion_inicial='Promovido',
    tutor_name=None,
    tutor_phone=None,
    tutor_relationship='Padre/Madre/Tutor',
    numero_orden=None
):
    """
    Actualiza la información de un estudiante existente y su familiar vinculado.
    """
    student = Student.query.get_or_404(student_id)
    
    student.first_name = first_name.strip()
    student.last_name = last_name.strip()
    student.section_id = section_id
    student.registration_number = registration_number.strip().upper()
    student.gender = gender
    student.birth_date = birth_date.strip() if birth_date else None
    student.condicion_inicial = condicion_inicial
    student.numero_orden = int(numero_orden) if numero_orden and str(numero_orden).isdigit() else student.numero_orden
    student.tutor_name = tutor_name.strip() if tutor_name else None
    student.tutor_phone = tutor_phone.strip() if tutor_phone else None
    student.tutor_relationship = tutor_relationship

    # Sincronizar o crear el registro Familiar
    if student.familiares:
        fam = student.familiares[0]
        fam.nombres = tutor_name.strip() if tutor_name else fam.nombres
        fam.parentesco = tutor_relationship
        fam.telefono = tutor_phone.strip() if tutor_phone else fam.telefono
        fam.whatsapp = tutor_phone.strip() if tutor_phone else fam.whatsapp
    elif tutor_name or tutor_phone:
        fam = Familiar(
            estudiante_id=student.id,
            nombres=tutor_name.strip() if tutor_name else f"Tutor de {student.full_name}",
            parentesco=tutor_relationship,
            telefono=tutor_phone.strip() if tutor_phone else None,
            whatsapp=tutor_phone.strip() if tutor_phone else None,
            es_contacto_principal=True,
            es_contacto_emergencia=True
        )
        db.session.add(fam)

    db.session.commit()
    return student

def update_student_phone(student_id, new_phone):
    """
    Actualiza el número de teléfono del estudiante y de sus familiares vinculados.
    """
    student = Student.query.get_or_404(student_id)
    clean_phone = new_phone.strip() if new_phone else None
    student.tutor_phone = clean_phone

    for fam in student.familiares:
        fam.telefono = clean_phone
        fam.whatsapp = clean_phone

    if not student.familiares and clean_phone:
        fam = Familiar(
            estudiante_id=student.id,
            nombres=student.tutor_name or f"Tutor de {student.full_name}",
            parentesco=student.tutor_relationship or 'Padre/Madre/Tutor',
            telefono=clean_phone,
            whatsapp=clean_phone,
            es_contacto_principal=True,
            es_contacto_emergencia=True
        )
        db.session.add(fam)

    db.session.commit()
    return student

def delete_student(student_id):
    """
    Elimina un estudiante del sistema junto a sus registros dependientes en cascada.
    """
    student = Student.query.get_or_404(student_id)
    full_name = student.full_name
    db.session.delete(student)
    db.session.commit()
    return full_name

def get_all_sections():
    """Retorna todas las secciones ordenadas por grado y nombre."""
    return Section.query.join(GradeLevel).order_by(GradeLevel.order, Section.name).all()

def get_all_grade_levels():
    """Retorna todos los grados académicos (1.º a 6.º)."""
    return GradeLevel.query.order_by(GradeLevel.order).all()

def get_all_cycles():
    """Retorna los ciclos de Secundaria (Primer y Segundo Ciclo)."""
    return Cycle.query.order_by(Cycle.id).all()

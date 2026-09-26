from datetime import date, timedelta
from app import db
from app.models.academic import Student, Section, GradeLevel, Cycle
from app.models.attendance import Attendance

# ── Mapas de estado P/T/A/E ─────────────────────────────────────────────────
STATUS_CODES = {
    'P': 'Presente',
    'T': 'Tardanza',
    'A': 'Ausente',
    'E': 'Excusa',
}
STATUS_LABELS = {v: k for k, v in STATUS_CODES.items()}

BADGE_CLASSES = {
    'Presente':  'bg-success',
    'Tardanza':  'bg-warning text-dark',
    'Ausente':   'bg-danger',
    'Excusa':    'bg-info text-dark',
    'P': 'bg-success',
    'T': 'bg-warning text-dark',
    'A': 'bg-danger',
    'E': 'bg-info text-dark',
}


# ── Consultas de asistencia individual ──────────────────────────────────────

def get_student_attendance_summary(student_id):
    """
    Retorna el resumen estadístico completo de asistencia de un estudiante:
    total P, T, A, E, porcentaje de asistencia y total de días registrados.
    """
    records   = Attendance.query.filter_by(student_id=student_id).all()
    total     = len(records)
    presentes = sum(1 for r in records if r.status in ('Presente', 'P'))
    tardanzas = sum(1 for r in records if r.status in ('Tardanza', 'T'))
    ausentes  = sum(1 for r in records if r.status in ('Ausente',  'A'))
    excusas   = sum(1 for r in records if r.status in ('Excusa',   'E'))

    dias_efectivos = presentes + excusas
    porcentaje = round((dias_efectivos / total * 100), 1) if total > 0 else 0.0

    return {
        'total':      total,
        'presentes':  presentes,
        'tardanzas':  tardanzas,
        'ausentes':   ausentes,
        'excusas':    excusas,
        'porcentaje': porcentaje,
        'has_alert':  ausentes >= 3,
    }


def get_student_absences_count(student_id):
    """Retorna el número total de ausencias de un estudiante."""
    return Attendance.query.filter(
        Attendance.student_id == student_id,
        Attendance.status.in_(('Ausente', 'A'))
    ).count()


def get_student_history(student_id, limit=60):
    """Retorna el historial de asistencia de un estudiante, más reciente primero."""
    return (
        Attendance.query
        .filter_by(student_id=student_id)
        .order_by(Attendance.date.desc())
        .limit(limit)
        .all()
    )


def get_attendance_for_date(student_id, target_date):
    """Devuelve el registro de asistencia de un estudiante en una fecha específica, o None."""
    return Attendance.query.filter_by(student_id=student_id, date=target_date).first()


# ── Registro / edición de asistencia ────────────────────────────────────────

def record_attendance_batch(student_status_dict, attendance_date=None, notes_dict=None):
    """
    Registra o actualiza la asistencia de una lista de estudiantes en una fecha dada.
    student_status_dict = {student_id: 'Presente'|'Tardanza'|'Ausente'|'Excusa'}
    """
    if attendance_date is None:
        attendance_date = date.today()
    if notes_dict is None:
        notes_dict = {}

    saved_count = 0
    for student_id, status in student_status_dict.items():
        full_status = STATUS_CODES.get(status, status)
        existing = Attendance.query.filter_by(student_id=student_id, date=attendance_date).first()
        note = notes_dict.get(str(student_id), '')
        codigo = STATUS_LABELS.get(full_status, full_status[0])

        if existing:
            existing.status        = full_status
            existing.codigo_estado = codigo
            if note:
                existing.notes = note
        else:
            new_att = Attendance(
                student_id=student_id,
                date=attendance_date,
                status=full_status,
                codigo_estado=codigo,
                notes=note
            )
            db.session.add(new_att)
        saved_count += 1

    db.session.commit()
    return saved_count


def record_single_attendance(student_id, att_date, status, notes=''):
    """Registra o actualiza la asistencia de un único estudiante."""
    full_status = STATUS_CODES.get(status, status)
    codigo      = STATUS_LABELS.get(full_status, status[0])
    existing    = Attendance.query.filter_by(student_id=student_id, date=att_date).first()
    if existing:
        existing.status        = full_status
        existing.codigo_estado = codigo
        existing.notes         = notes
        db.session.commit()
        return existing
    else:
        att = Attendance(
            student_id=student_id,
            date=att_date,
            status=full_status,
            codigo_estado=codigo,
            notes=notes
        )
        db.session.add(att)
        db.session.commit()
        return att


def delete_attendance_record(attendance_id):
    """Elimina un registro individual de asistencia."""
    att = Attendance.query.get_or_404(attendance_id)
    db.session.delete(att)
    db.session.commit()


# ── Alertas ──────────────────────────────────────────────────────────────────

def get_students_with_alerts():
    """
    Regla Específica EduReport:
    Identifica a todos los estudiantes con 3 o más ausencias acumuladas.
    Devuelve lista con student, absences_count, absences[], section, grade, cycle, summary.
    """
    students = Student.query.filter_by(is_active=True).all()
    alert_list = []
    for s in students:
        absences = [a for a in s.asistencias if a.status in ('Ausente', 'A')]
        if len(absences) >= 3:
            alert_list.append({
                'student':        s,
                'absences_count': len(absences),
                'absences':       sorted(absences, key=lambda a: a.date, reverse=True),
                'section':        s.section,
                'grade':          s.section.grade_level,
                'cycle':          s.section.grade_level.cycle,
                'summary':        get_student_attendance_summary(s.id),
            })
    alert_list.sort(key=lambda x: x['absences_count'], reverse=True)
    return alert_list


# ── Estadísticas globales ────────────────────────────────────────────────────

def get_attendance_stats():
    """Calcula métricas agregadas de asistencia para los gráficos del dashboard."""
    total_present  = Attendance.query.filter(Attendance.status.in_(('Presente', 'P'))).count()
    total_absent   = Attendance.query.filter(Attendance.status.in_(('Ausente',  'A'))).count()
    total_tardy    = Attendance.query.filter(Attendance.status.in_(('Tardanza', 'T'))).count()
    total_excused  = Attendance.query.filter(Attendance.status.in_(('Excusa',   'E'))).count()
    total_records  = total_present + total_absent + total_tardy + total_excused

    dias_efectivos    = total_present + total_excused
    porcentaje_global = round((dias_efectivos / total_records * 100), 1) if total_records > 0 else 0.0

    c1_students = (
        Student.query
        .join(Section, Student.section_id == Section.id)
        .join(GradeLevel, Section.grade_id == GradeLevel.id)
        .join(Cycle, GradeLevel.cycle_id == Cycle.id)
        .filter(Cycle.name == 'Primer Ciclo')
        .all()
    )
    c2_students = (
        Student.query
        .join(Section, Student.section_id == Section.id)
        .join(GradeLevel, Section.grade_id == GradeLevel.id)
        .join(Cycle, GradeLevel.cycle_id == Cycle.id)
        .filter(Cycle.name == 'Segundo Ciclo')
        .all()
    )

    c1_alerts = sum(1 for s in c1_students if s.total_absences >= 3)
    c2_alerts = sum(1 for s in c2_students if s.total_absences >= 3)

    return {
        'total_present':     total_present,
        'total_absent':      total_absent,
        'total_tardy':       total_tardy,
        'total_excused':     total_excused,
        'total_records':     total_records,
        'porcentaje_global': porcentaje_global,
        'c1_alerts':         c1_alerts,
        'c2_alerts':         c2_alerts,
        'c1_total_students': len(c1_students),
        'c2_total_students': len(c2_students),
    }


def get_section_attendance_for_date(section_id, target_date):
    """
    Retorna lista de estudiantes de una sección con su estado de asistencia
    para una fecha específica.
    """
    section = Section.query.get(section_id)
    if not section:
        return []
    result = []
    for s in section.estudiantes:
        existing = Attendance.query.filter_by(student_id=s.id, date=target_date).first()
        result.append({
            'student':        s,
            'current_status': existing.status if existing else None,
            'current_note':   existing.notes  if existing else '',
            'record_id':      existing.id     if existing else None,
            'total_absences': s.total_absences,
            'has_alert':      s.has_absence_alert,
            'summary':        get_student_attendance_summary(s.id),
        })
    return result


# ── Datos ficticios de prueba ────────────────────────────────────────────────

def seed_demo_attendance():
    """
    Inserta datos ficticios de asistencia para demostrar la Regla de 3 Ausencias.
    Patrón: los primeros 3 estudiantes acumulan 3+ ausencias para activar alertas.
    """
    students = Student.query.limit(10).all()
    if not students:
        return 0

    today = date.today()
    seeded = 0

    demo_patterns = [
        # Estudiante 0: 3 ausencias → alerta activa
        [(-10, 'Presente'), (-9, 'Presente'), (-8, 'Ausente'),
         (-7,  'Tardanza'), (-6, 'Ausente'),  (-5, 'Presente'),
         (-4,  'Ausente'),  (-3, 'Excusa'),   (-2, 'Presente'), (-1, 'Presente')],
        # Estudiante 1: 4 ausencias → alerta crítica
        [(-8, 'Ausente'),  (-7, 'Ausente'),  (-6, 'Ausente'),
         (-5, 'Presente'), (-4, 'Tardanza'), (-3, 'Presente'), (-2, 'Ausente')],
        # Estudiante 2: 0 ausencias → sin alerta
        [(-6, 'Presente'), (-5, 'Presente'), (-4, 'Presente'),
         (-3, 'Tardanza'), (-2, 'Excusa'),   (-1, 'Presente')],
        # Patrón genérico para el resto
        [(-5, 'Presente'), (-4, 'Tardanza'), (-3, 'Presente'),
         (-2, 'Presente'), (-1, 'Excusa')],
    ]

    for i, student in enumerate(students):
        pattern = demo_patterns[min(i, len(demo_patterns) - 1)]
        for offset, status in pattern:
            att_date = today + timedelta(days=offset)
            exists = Attendance.query.filter_by(
                student_id=student.id, date=att_date
            ).first()
            if not exists:
                codigo = STATUS_LABELS.get(status, status[0])
                att = Attendance(
                    student_id=student.id,
                    date=att_date,
                    status=status,
                    codigo_estado=codigo,
                    notes='[Demo]'
                )
                db.session.add(att)
                seeded += 1
    db.session.commit()
    return seeded

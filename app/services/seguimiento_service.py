from datetime import date
from app import db
from app.models.academic import Student
from app.models.evaluation import Seguimiento, Reporte

TIPOS_SEGUIMIENTO = [
    'Asistencia',
    'Academico',
    'Conductual',
    'Reconocimiento',
    'General',
]
ESTADOS_SEGUIMIENTO = ['Abierto', 'En Proceso', 'Resuelto', 'Cerrado']

def get_seguimientos_estudiante(student_id):
    return (
        Seguimiento.query
        .filter_by(student_id=student_id)
        .order_by(Seguimiento.fecha.desc())
        .all()
    )

def get_all_seguimientos():
    return (
        Seguimiento.query
        .order_by(Seguimiento.fecha.desc())
        .limit(100)
        .all()
    )

def get_seguimiento(seg_id):
    return Seguimiento.query.get_or_404(seg_id)

def save_seguimiento(student_id, aula_id, fecha_str, tipo, motivo,
                     descripcion, acciones, status, responsable,
                     fecha_resolucion_str=None, seg_id=None):
    try:
        from datetime import datetime
        fecha = datetime.strptime(fecha_str, '%Y-%m-%d').date()
    except (ValueError, TypeError):
        fecha = date.today()

    fecha_res = None
    if fecha_resolucion_str and str(fecha_resolucion_str).strip():
        try:
            from datetime import datetime
            fecha_res = datetime.strptime(fecha_resolucion_str, '%Y-%m-%d').date()
        except ValueError:
            pass

    if seg_id:
        seg = Seguimiento.query.get_or_404(seg_id)
    else:
        seg = Seguimiento(student_id=student_id)
        db.session.add(seg)

    seg.aula_id          = aula_id
    seg.fecha            = fecha
    seg.tipo             = tipo
    seg.motivo           = motivo
    seg.descripcion      = descripcion
    seg.acciones_acordadas = acciones
    seg.status           = status
    seg.responsable      = responsable
    seg.fecha_resolucion = fecha_res
    db.session.commit()
    return seg

def delete_seguimiento(seg_id):
    seg = Seguimiento.query.get_or_404(seg_id)
    db.session.delete(seg)
    db.session.commit()

def get_seguimiento_stats():
    total   = Seguimiento.query.count()
    abiertos = Seguimiento.query.filter_by(status='Abierto').count()
    en_proceso = Seguimiento.query.filter_by(status='En Proceso').count()
    resueltos  = Seguimiento.query.filter_by(status='Resuelto').count()
    por_tipo = {}
    for tipo in TIPOS_SEGUIMIENTO:
        por_tipo[tipo] = Seguimiento.query.filter_by(tipo=tipo).count()
    return {
        'total': total,
        'abiertos': abiertos,
        'en_proceso': en_proceso,
        'resueltos': resueltos,
        'por_tipo': por_tipo,
    }

# ── Reportes ─────────────────────────────────────────────────────────────────

TIPOS_REPORTE = [
    'Seguimiento de Asistencia',
    'Avance Academico',
    'Bajo Rendimiento',
    'Progreso Academico',
    'Reconocimiento Positivo',
    'Seguimiento Integral',
]

def get_all_reportes():
    return Reporte.query.order_by(Reporte.fecha_generacion.desc()).all()

def get_reportes_estudiante(student_id):
    return Reporte.query.filter_by(estudiante_id=student_id).order_by(Reporte.fecha_generacion.desc()).all()

def save_reporte(tipo_reporte, titulo, estudiante_id=None, aula_id=None,
                 periodo=None, generado_por='Sistema EduReport', datos_json=None):
    rep = Reporte(
        tipo_reporte=tipo_reporte,
        titulo=titulo,
        estudiante_id=estudiante_id,
        aula_id=aula_id,
        periodo=periodo,
        generado_por=generado_por,
        datos_json=datos_json,
    )
    db.session.add(rep)
    db.session.commit()
    return rep

def seed_demo_seguimientos():
    from app.services.attendance_service import get_students_with_alerts
    alerts = get_students_with_alerts()
    count = 0
    for item in alerts:
        s = item['student']
        exists = Seguimiento.query.filter_by(student_id=s.id, tipo='Asistencia').first()
        if not exists:
            seg = Seguimiento(
                student_id=s.id,
                aula_id=s.section_id,
                fecha=date.today(),
                tipo='Asistencia',
                motivo=f'El estudiante ha acumulado {item["absences_count"]} ausencias (>=3). Se activa alerta automatica.',
                descripcion=f'Seguimiento generado automaticamente por EduReport al detectar {item["absences_count"]} ausencias acumuladas.',
                acciones_acordadas='1. Notificar al tutor via WhatsApp.\n2. Citar al padre/madre/tutor al centro.\n3. Registrar compromiso de asistencia.\n4. Seguimiento semanal.',
                status='Abierto',
                responsable='Departamento de Orientacion y Psicologia',
            )
            db.session.add(seg)
            count += 1
    db.session.commit()
    return count

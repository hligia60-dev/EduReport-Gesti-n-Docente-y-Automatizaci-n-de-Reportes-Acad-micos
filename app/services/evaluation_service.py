from app import db
from app.models.academic import Student, Section, GradeLevel, Cycle
from app.models.evaluation import Asignatura, Evaluacion, Seguimiento, Reporte

PERIODS = ['P1', 'P2', 'P3', 'P4']

# ── Asignaturas ──────────────────────────────────────────────────────────────

def get_all_asignaturas():
    return Asignatura.query.order_by(Asignatura.nombre).all()

def get_asignatura(asig_id):
    return Asignatura.query.get_or_404(asig_id)

# ── Evaluaciones ─────────────────────────────────────────────────────────────

def get_evaluaciones_estudiante(student_id):
    """Devuelve evaluaciones agrupadas por asignatura y período."""
    evaluaciones = (
        Evaluacion.query
        .filter_by(student_id=student_id)
        .order_by(Evaluacion.asignatura_id, Evaluacion.period)
        .all()
    )
    return evaluaciones

def get_evaluaciones_by_period(student_id, period):
    return (
        Evaluacion.query
        .filter_by(student_id=student_id, period=period)
        .order_by(Evaluacion.asignatura_id)
        .all()
    )

def get_evaluacion(eval_id):
    return Evaluacion.query.get_or_404(eval_id)

def save_evaluacion(student_id, asignatura_id, period, score,
                    calificacion_recuperacion=None, observaciones=None,
                    indicator_id=None, eval_id=None):
    """Crea o actualiza una evaluación."""
    score = float(score)
    cal_rec = float(calificacion_recuperacion) if calificacion_recuperacion is not None and str(calificacion_recuperacion).strip() != '' else None
    cal_final = max(score, cal_rec) if cal_rec is not None else score
    aprobado  = cal_final >= 70

    if eval_id:
        ev = Evaluacion.query.get_or_404(eval_id)
    else:
        ev = Evaluacion.query.filter_by(
            student_id=student_id, asignatura_id=asignatura_id, period=period
        ).first()
        if not ev:
            ev = Evaluacion(student_id=student_id, asignatura_id=asignatura_id, period=period)
            db.session.add(ev)

    ev.score                    = score
    ev.calificacion_recuperacion = cal_rec
    ev.calificacion_final_periodo = cal_final
    ev.aprobado                 = aprobado
    ev.observaciones            = observaciones
    if indicator_id:
        ev.indicator_id = indicator_id
    db.session.commit()
    return ev

def delete_evaluacion(eval_id):
    ev = Evaluacion.query.get_or_404(eval_id)
    db.session.delete(ev)
    db.session.commit()

# ── Promedios y evolución ────────────────────────────────────────────────────

def get_student_academic_summary(student_id):
    """
    Retorna resumen académico del estudiante:
    - promedio general, promedios por período, por asignatura y estado de aprobación.
    """
    evs = Evaluacion.query.filter_by(student_id=student_id).all()
    if not evs:
        return {
            'promedio_general': 0,
            'total_evaluaciones': 0,
            'aprobadas': 0,
            'reprobadas': 0,
            'en_recuperacion': 0,
            'por_periodo': {p: {'promedio': 0, 'count': 0} for p in PERIODS},
            'por_asignatura': [],
            'evolucion_chart': {'labels': PERIODS, 'data': [0, 0, 0, 0]},
        }

    totales = [ev.calificacion_final_periodo or ev.score for ev in evs]
    promedio_general = round(sum(totales) / len(totales), 1) if totales else 0

    por_periodo = {}
    for p in PERIODS:
        p_evs = [ev for ev in evs if ev.period == p]
        if p_evs:
            vals = [ev.calificacion_final_periodo or ev.score for ev in p_evs]
            por_periodo[p] = {'promedio': round(sum(vals) / len(vals), 1), 'count': len(p_evs)}
        else:
            por_periodo[p] = {'promedio': 0, 'count': 0}

    # Por asignatura
    asig_map = {}
    for ev in evs:
        asig_id = ev.asignatura_id
        if asig_id not in asig_map:
            asig_map[asig_id] = {'asignatura': ev.asignatura, 'evaluaciones': []}
        asig_map[asig_id]['evaluaciones'].append(ev)

    por_asignatura = []
    for asig_id, data in asig_map.items():
        asig_evs = data['evaluaciones']
        vals = [ev.calificacion_final_periodo or ev.score for ev in asig_evs]
        promedio = round(sum(vals) / len(vals), 1)
        por_asignatura.append({
            'asignatura': data['asignatura'],
            'promedio':   promedio,
            'aprobada':   promedio >= 70,
            'evaluaciones': sorted(asig_evs, key=lambda e: e.period),
            'por_periodo': {ev.period: ev for ev in asig_evs},
        })
    por_asignatura.sort(key=lambda x: x['asignatura'].nombre)

    return {
        'promedio_general':   promedio_general,
        'total_evaluaciones': len(evs),
        'aprobadas':          sum(1 for ev in evs if ev.aprobado),
        'reprobadas':         sum(1 for ev in evs if not ev.aprobado),
        'en_recuperacion':    sum(1 for ev in evs if ev.calificacion_recuperacion is not None),
        'por_periodo':        por_periodo,
        'por_asignatura':     por_asignatura,
        'evolucion_chart': {
            'labels': PERIODS,
            'data': [por_periodo[p]['promedio'] for p in PERIODS],
        },
    }

# ── Dashboard académico global ───────────────────────────────────────────────

def get_academic_global_stats():
    """Estadísticas académicas globales para el dashboard."""
    evs = Evaluacion.query.all()
    if not evs:
        return {
            'promedio_global': 0,
            'total_evaluaciones': 0,
            'aprobadas': 0,
            'reprobadas': 0,
            'en_recuperacion': 0,
            'bajo_rendimiento_count': 0,
            'con_progreso_count': 0,
        }
    totales = [ev.calificacion_final_periodo or ev.score for ev in evs]
    promedio_global = round(sum(totales) / len(totales), 1)

    # Estudiantes con promedio < 70 en alguna asignatura
    students = Student.query.filter_by(is_active=True).all()
    bajo_rendimiento = 0
    con_progreso = 0
    for s in students:
        s_evs = [ev for ev in s.evaluaciones]
        if not s_evs:
            continue
        vals = [ev.calificacion_final_periodo or ev.score for ev in s_evs]
        prom = sum(vals) / len(vals)
        if prom < 70:
            bajo_rendimiento += 1
        else:
            con_progreso += 1

    return {
        'promedio_global':      promedio_global,
        'total_evaluaciones':   len(evs),
        'aprobadas':            sum(1 for ev in evs if ev.aprobado),
        'reprobadas':           sum(1 for ev in evs if not ev.aprobado),
        'en_recuperacion':      sum(1 for ev in evs if ev.calificacion_recuperacion is not None),
        'bajo_rendimiento_count': bajo_rendimiento,
        'con_progreso_count':     con_progreso,
    }

# ── Seed de datos demo de evaluaciones ─────────────────────────────────────

def seed_demo_evaluaciones():
    """Inserta calificaciones ficticias para demostrar la evolución académica."""
    from datetime import datetime
    students = Student.query.limit(6).all()
    asignaturas = Asignatura.query.limit(5).all()
    if not students or not asignaturas:
        return 0
    count = 0
    import random
    random.seed(42)
    for st in students:
        for asig in asignaturas:
            for period in PERIODS:
                exists = Evaluacion.query.filter_by(
                    student_id=st.id, asignatura_id=asig.id, period=period
                ).first()
                if not exists:
                    base = random.randint(55, 98)
                    rec = random.randint(60, 75) if base < 70 else None
                    ev = Evaluacion(
                        student_id=st.id,
                        asignatura_id=asig.id,
                        period=period,
                        score=float(base),
                        calificacion_recuperacion=float(rec) if rec else None,
                        calificacion_final_periodo=float(max(base, rec)) if rec else float(base),
                        aprobado=(max(base, rec) if rec else base) >= 70,
                        observaciones='[Demo]'
                    )
                    db.session.add(ev)
                    count += 1
    db.session.commit()
    return count

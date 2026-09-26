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

def save_evaluacion(student_id, asignatura_id, period, score=None,
                    calificacion_recuperacion=None, observaciones=None,
                    indicator_id=None, eval_id=None,
                    c1_score=None, c2_score=None, c3_score=None, c4_score=None,
                    c1_rp=None, c2_rp=None, c3_rp=None, c4_rp=None):
    """Crea o actualiza una evaluación con las 4 competencias ordinarias y sus 4 casillas de RP."""
    
    # Procesar calificaciones ordinarias por competencia
    def _to_float_or_none(val):
        if val is None or str(val).strip() == '':
            return None
        try:
            return float(val)
        except (ValueError, TypeError):
            return None

    c1_s = _to_float_or_none(c1_score)
    c2_s = _to_float_or_none(c2_score)
    c3_s = _to_float_or_none(c3_score)
    c4_s = _to_float_or_none(c4_score)

    # Si se pasaron las 4 notas ordinarias
    if c1_s is not None or c2_s is not None or c3_s is not None or c4_s is not None:
        c1_s = c1_s if c1_s is not None else 0.0
        c2_s = c2_s if c2_s is not None else 0.0
        c3_s = c3_s if c3_s is not None else 0.0
        c4_s = c4_s if c4_s is not None else 0.0
        score = round((c1_s + c2_s + c3_s + c4_s) / 4.0, 1)
    else:
        score = float(score) if score is not None else 0.0
        c1_s = c2_s = c3_s = c4_s = score

    # Procesar las 4 casillas de RP
    c1_r = _to_float_or_none(c1_rp)
    c2_r = _to_float_or_none(c2_rp)
    c3_r = _to_float_or_none(c3_rp)
    c4_r = _to_float_or_none(c4_rp)

    # Calcular nota final por cada competencia (si tiene RP y es mayor, se toma la RP)
    f1 = max(c1_s, c1_r) if c1_r is not None else c1_s
    f2 = max(c2_s, c2_r) if c2_r is not None else c2_s
    f3 = max(c3_s, c3_r) if c3_r is not None else c3_s
    f4 = max(c4_s, c4_r) if c4_r is not None else c4_s

    cal_final = round((f1 + f2 + f3 + f4) / 4.0, 1)

    # Promedio o registro de recuperación pedagógica global
    rps = [r for r in (c1_r, c2_r, c3_r, c4_r) if r is not None]
    if rps:
        cal_rec = round(sum(rps) / len(rps), 1)
    else:
        cal_rec = _to_float_or_none(calificacion_recuperacion)
        if cal_rec is not None:
            cal_final = max(score, cal_rec)

    aprobado = cal_final >= 70

    if eval_id:
        ev = Evaluacion.query.get_or_404(eval_id)
    else:
        ev = Evaluacion.query.filter_by(
            student_id=student_id, asignatura_id=asignatura_id, period=period
        ).first()
        if not ev:
            ev = Evaluacion(student_id=student_id, asignatura_id=asignatura_id, period=period)
            db.session.add(ev)

    ev.c1_score = c1_s
    ev.c2_score = c2_s
    ev.c3_score = c3_s
    ev.c4_score = c4_s

    ev.c1_rp = c1_r
    ev.c2_rp = c2_r
    ev.c3_rp = c3_r
    ev.c4_rp = c4_r

    ev.score = score
    ev.calificacion_recuperacion = cal_rec
    ev.calificacion_final_periodo = cal_final
    ev.aprobado = aprobado
    ev.observaciones = observaciones
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

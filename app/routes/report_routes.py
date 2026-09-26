from io import BytesIO
from datetime import date
from flask import Blueprint, render_template, request, redirect, url_for, flash, send_file
from app import db
from app.models.academic import Student, Section
from app.models.evaluation import Asignatura, Evaluacion, Reporte
from app.services import attendance_service, student_service
from app.services.evaluation_service import get_student_academic_summary, get_all_asignaturas, PERIODS
from app.services.seguimiento_service import save_reporte, TIPOS_REPORTE
from app.services.pdf_service import generate_official_pdf, build_report_data_from_student, get_default_institutional_data

report_bp = Blueprint('reports', __name__, url_prefix='/reportes')


@report_bp.route('/')
def index():
    """Centro general de reportes."""
    alerts       = attendance_service.get_students_with_alerts()
    students     = student_service.get_all_students()
    sections     = student_service.get_all_sections()
    asignaturas  = get_all_asignaturas()
    reportes     = Reporte.query.order_by(Reporte.fecha_generacion.desc()).limit(20).all()
    return render_template('reports/index.html',
                           alerts=alerts, students=students,
                           sections=sections, asignaturas=asignaturas,
                           reportes=reportes, tipos=TIPOS_REPORTE, periods=PERIODS)


# ── Generador de borrador ────────────────────────────────────────────────────

@report_bp.route('/generar', methods=['GET', 'POST'])
def generar():
    """
    Paso 1: Seleccion de parametros del reporte.
    Paso 2: Vista previa del borrador (editable antes de imprimir).
    """
    students    = student_service.get_all_students()
    sections    = student_service.get_all_sections()
    asignaturas = get_all_asignaturas()

    if request.method == 'POST':
        tipo_reporte = request.form.get('tipo_reporte', '').strip()
        student_id   = request.form.get('student_id', type=int)
        section_id   = request.form.get('section_id', type=int)
        asignatura_id= request.form.get('asignatura_id', type=int)
        period       = request.form.get('period', '').strip()
        texto_extra  = request.form.get('texto_extra', '').strip()

        student  = Student.query.get(student_id) if student_id else None
        section  = Section.query.get(section_id) if section_id else None
        asig     = Asignatura.query.get(asignatura_id) if asignatura_id else None

        # Construir borrador con datos reales
        borrador = _build_borrador(tipo_reporte, student, section, asig, period, texto_extra)

        return render_template('reports/preview.html',
                               tipo_reporte=tipo_reporte,
                               student=student, section=section,
                               asig=asig, period=period,
                               borrador=borrador,
                               students=students, sections=sections,
                               asignaturas=asignaturas, periods=PERIODS,
                               current_date=date.today())

    return render_template('reports/generar.html',
                           students=students, sections=sections,
                           asignaturas=asignaturas, periods=PERIODS,
                           tipos=TIPOS_REPORTE)


@report_bp.route('/imprimir', methods=['POST'])
def imprimir():
    """
    Paso 3: Imprimir / guardar PDF del reporte finalizado.
    Guarda un registro en la tabla Reporte.
    """
    tipo_reporte = request.form.get('tipo_reporte', '').strip()
    student_id   = request.form.get('student_id', type=int)
    section_id   = request.form.get('section_id', type=int)
    period       = request.form.get('period', '').strip()
    texto_final  = request.form.get('texto_final', '').strip()

    student = Student.query.get(student_id) if student_id else None
    titulo  = f'{tipo_reporte} — {student.full_name if student else "General"} — {period or "Todos los periodos"}'

    rep = save_reporte(
        tipo_reporte=tipo_reporte,
        titulo=titulo,
        estudiante_id=student_id,
        aula_id=section_id or (student.section_id if student else None),
        periodo=period,
        generado_por='EduReport',
        datos_json=texto_final[:2000] if texto_final else None,
    )

    return render_template('reports/print_view.html',
                           tipo_reporte=tipo_reporte,
                           student=student,
                           period=period,
                           texto_final=texto_final,
                           reporte_id=rep.id,
                           current_date=date.today())


# ── Informe de asistencia (desde alerta) ────────────────────────────────────

@report_bp.route('/asistencia/<int:student_id>')
def attendance_report(student_id):
    """Informe oficial de seguimiento de asistencia para imprimir/PDF."""
    student   = Student.query.get_or_404(student_id)
    absences  = sorted(
        [a for a in student.asistencias if a.status in ('Ausente', 'A')],
        key=lambda a: a.date
    )
    return render_template('reports/attendance_report.html',
                           student=student,
                           absences=absences,
                           total_absences=len(absences),
                           current_date=date.today(),
                           has_alert=len(absences) >= 3)


# ── Descarga de PDF con ReportLab ──────────────────────────────────────────

@report_bp.route('/estudiante/<int:student_id>/pdf')
def descargar_pdf_estudiante(student_id):
    """Genera y descarga un informe oficial en formato PDF para un estudiante."""
    student = Student.query.get_or_404(student_id)
    tipo = request.args.get('tipo', 'Seguimiento de Asistencia').strip()
    period = request.args.get('period', 'P1').strip()
    asignatura_id = request.args.get('asignatura_id', type=int)
    asig = Asignatura.query.get(asignatura_id) if asignatura_id else None

    data = build_report_data_from_student(
        tipo_reporte=tipo,
        student=student,
        asignatura=asig,
        periodo=period
    )
    pdf_bytes = generate_official_pdf(data)

    safe_name = f"EduReport_{tipo.replace(' ', '_')}_{student.registration_number}.pdf"
    return send_file(
        BytesIO(pdf_bytes),
        mimetype='application/pdf',
        as_attachment=True,
        download_name=safe_name
    )


@report_bp.route('/descargar-pdf', methods=['POST'])
def descargar_pdf():
    """Genera y descarga el PDF a partir de los datos editados en la vista previa."""
    tipo_reporte = request.form.get('tipo_reporte', 'Informe Oficial').strip()
    student_id = request.form.get('student_id', type=int)
    period = request.form.get('period', 'P1').strip()
    texto_final = request.form.get('texto_final', '').strip()

    student = Student.query.get(student_id) if student_id else None
    data = build_report_data_from_student(
        tipo_reporte=tipo_reporte,
        student=student,
        periodo=period,
        observaciones_docente=texto_final if texto_final else None
    )

    pdf_bytes = generate_official_pdf(data)
    reg_num = student.registration_number if student else "General"
    safe_name = f"EduReport_{tipo_reporte.replace(' ', '_')}_{reg_num}.pdf"

    return send_file(
        BytesIO(pdf_bytes),
        mimetype='application/pdf',
        as_attachment=True,
        download_name=safe_name
    )


@report_bp.route('/pdf/<int:reporte_id>')
def descargar_pdf_reporte(reporte_id):
    """Genera el PDF correspondiente a un reporte guardado en la base de datos."""
    rep = Reporte.query.get_or_404(reporte_id)
    student = Student.query.get(rep.estudiante_id) if rep.estudiante_id else None
    data = build_report_data_from_student(
        tipo_reporte=rep.tipo_reporte,
        student=student,
        periodo=rep.periodo or 'P1',
        observaciones_docente=rep.datos_json
    )
    data['asunto'] = rep.titulo or rep.tipo_reporte

    pdf_bytes = generate_official_pdf(data)
    safe_name = f"Reporte_{rep.id}_{rep.tipo_reporte.replace(' ', '_')}.pdf"

    return send_file(
        BytesIO(pdf_bytes),
        mimetype='application/pdf',
        as_attachment=True,
        download_name=safe_name
    )


@report_bp.route('/eliminar/<int:reporte_id>', methods=['POST'])
def eliminar_reporte(reporte_id):
    """
    Elimina un reporte generado de la base de datos.
    Permite anular reportes emitidos por error o descartar versiones previas al regenerar.
    """
    rep = Reporte.query.get_or_404(reporte_id)
    titulo = rep.titulo or f"Reporte #{rep.id}"
    student_id = rep.estudiante_id
    db.session.delete(rep)
    db.session.commit()
    flash(f'El reporte "{titulo}" ha sido eliminado exitosamente.', 'info')

    next_url = request.form.get('next')
    if next_url:
        return redirect(next_url)
    if student_id:
        return redirect(url_for('students.detail', student_id=student_id))
    return redirect(url_for('reports.index'))


# ── Constructor de borradores ────────────────────────────────────────────────

def _build_borrador(tipo, student, section, asig, period, texto_extra=''):
    """
    Genera un borrador de texto basado unicamente en datos reales.
    NO inventa hechos: si no hay datos, lo indica explicitamente.
    """
    lines = []
    today_str = date.today().strftime('%d/%m/%Y')

    if tipo == 'Seguimiento de Asistencia' and student:
        absences = [a for a in student.asistencias if a.status in ('Ausente','A')]
        lines += [
            f'Fecha de emision: {today_str}',
            f'',
            f'INFORME DE SEGUIMIENTO DE ASISTENCIA',
            f'',
            f'Estudiante: {student.full_name}',
            f'RNE/Matricula: {student.registration_number}',
            f'Seccion: {student.section.nombre or student.section.name}',
            f'Tutor: {student.tutor_name or "No registrado"} — {student.tutor_phone or "Sin telefono"}',
            f'',
            f'Situacion detectada:',
            f'El/la estudiante ha acumulado {len(absences)} ausencia(s) a la fecha de emision de este informe.',
        ]
        if absences:
            lines.append('Fechas de ausencias registradas:')
            for a in absences:
                obs = f' ({a.notes})' if a.notes and a.notes != '[Demo]' else ''
                lines.append(f'  - {a.date.strftime("%d/%m/%Y")}{obs}')
        lines += [
            '',
            'Recomendaciones:',
            '1. Comunicar la situacion al padre, madre o tutor legal.',
            '2. Registrar el compromiso de asistencia en el expediente.',
            '3. Realizar seguimiento semanal.',
        ]

    elif tipo == 'Avance Academico' and student:
        summary = get_student_academic_summary(student.id)
        lines += [
            f'Fecha de emision: {today_str}',
            f'',
            f'INFORME DE AVANCE ACADEMICO',
            f'',
            f'Estudiante: {student.full_name}',
            f'RNE/Matricula: {student.registration_number}',
            f'Seccion: {student.section.nombre or student.section.name}',
            f'Promedio general: {summary["promedio_general"]} puntos',
            f'',
            'Promedios por periodo:',
        ]
        for p in PERIODS:
            pdata = summary['por_periodo'].get(p, {})
            prom  = pdata.get('promedio', 0)
            if prom > 0:
                lines.append(f'  {p}: {prom} puntos — {"APROBADO" if prom >= 70 else "REPROBADO"}')
        if period:
            p_evs = [ev for ev in student.evaluaciones if ev.period == period]
            if p_evs:
                lines += ['', f'Detalle de calificaciones en {period}:']
                for ev in p_evs:
                    rec_str = f' | RP: {ev.calificacion_recuperacion}' if ev.calificacion_recuperacion else ''
                    lines.append(f'  - {ev.asignatura.nombre}: {ev.score}{rec_str} → Final: {ev.calificacion_final_periodo or ev.score}')

    elif tipo == 'Bajo Rendimiento' and student:
        summary = get_student_academic_summary(student.id)
        bajo = [a for a in summary.get('por_asignatura', []) if not a['aprobada']]
        lines += [
            f'Fecha de emision: {today_str}',
            '',
            'INFORME DE BAJO RENDIMIENTO ACADEMICO',
            '',
            f'Estudiante: {student.full_name}',
            f'RNE/Matricula: {student.registration_number}',
            f'Seccion: {student.section.nombre or student.section.name}',
            f'Promedio general: {summary["promedio_general"]}',
            '',
            f'Asignaturas con promedio menor a 70:',
        ]
        if bajo:
            for a in bajo:
                lines.append(f'  - {a["asignatura"].nombre}: {a["promedio"]} puntos')
        else:
            lines.append('  (No se encontraron asignaturas reprobadas en el sistema.)')
        lines += ['', 'Recomendaciones:', '1. Refuerzo pedagogico en las asignaturas identificadas.',
                  '2. Plan de recuperacion pedagogica (RP) segun normativa.']

    elif tipo == 'Progreso Academico' and student:
        summary = get_student_academic_summary(student.id)
        lines += [
            f'Fecha de emision: {today_str}', '',
            'INFORME DE PROGRESO ACADEMICO', '',
            f'Estudiante: {student.full_name}',
            f'RNE/Matricula: {student.registration_number}',
            f'Promedio general: {summary["promedio_general"]}',
            f'Evaluaciones aprobadas: {summary["aprobadas"]} de {summary["total_evaluaciones"]}',
            '',
            'Evolucion por periodo:',
        ]
        prev = None
        for p in PERIODS:
            prom = summary['por_periodo'].get(p, {}).get('promedio', 0)
            if prom > 0:
                tendencia = ''
                if prev is not None:
                    tendencia = ' ↑ Mejora' if prom > prev else (' ↓ Descenso' if prom < prev else ' → Estable')
                lines.append(f'  {p}: {prom}{tendencia}')
                prev = prom

    elif tipo == 'Reconocimiento Positivo' and student:
        summary = get_student_academic_summary(student.id)
        att_summary = attendance_service.get_student_attendance_summary(student.id)
        lines += [
            f'Fecha de emision: {today_str}', '',
            'RECONOCIMIENTO POSITIVO', '',
            f'Estudiante: {student.full_name}',
            f'RNE/Matricula: {student.registration_number}',
            f'Seccion: {student.section.nombre or student.section.name}', '',
            f'Promedio academico: {summary["promedio_general"]} puntos.',
            f'Porcentaje de asistencia: {att_summary["porcentaje"]}%.',
            '',
            'El/La estudiante ha mostrado un desempeno destacado en el periodo evaluado.',
            'Se emite el presente reconocimiento conforme a los criterios establecidos por el MINERD.',
        ]

    elif tipo == 'Seguimiento Integral' and student:
        summary     = get_student_academic_summary(student.id)
        att_summary = attendance_service.get_student_attendance_summary(student.id)
        segs        = student.seguimientos
        lines += [
            f'Fecha de emision: {today_str}', '',
            'INFORME DE SEGUIMIENTO INTEGRAL', '',
            f'Estudiante: {student.full_name}',
            f'RNE: {student.registration_number}',
            f'Seccion: {student.section.nombre or student.section.name}',
            f'Tutor: {student.tutor_name or "No registrado"}', '',
            'ASISTENCIA:',
            f'  P: {att_summary["presentes"]}  T: {att_summary["tardanzas"]}  A: {att_summary["ausentes"]}  E: {att_summary["excusas"]}',
            f'  Porcentaje: {att_summary["porcentaje"]}%',
            '',
            f'RENDIMIENTO ACADEMICO:',
            f'  Promedio general: {summary["promedio_general"]}',
            f'  Aprobadas: {summary["aprobadas"]} / {summary["total_evaluaciones"]}',
            '',
            f'SEGUIMIENTOS PREVIOS REGISTRADOS: {len(segs)}',
        ]
        for seg in segs[:3]:
            lines.append(f'  [{seg.fecha.strftime("%d/%m/%Y") if seg.fecha else "?"}] {seg.tipo}: {seg.motivo}')

    else:
        lines += [
            f'Fecha de emision: {today_str}', '',
            f'REPORTE: {tipo}', '',
            'No se encontraron datos suficientes para generar el informe.',
            'Por favor, seleccione un estudiante y/o parametros adicionales.',
        ]

    if texto_extra:
        lines += ['', 'OBSERVACION ADICIONAL DEL DOCENTE:', texto_extra]

    return '\n'.join(lines)

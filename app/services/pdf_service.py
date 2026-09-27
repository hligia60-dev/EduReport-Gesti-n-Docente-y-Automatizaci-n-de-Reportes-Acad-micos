"""
Módulo de Generación de Informes Oficiales en PDF usando ReportLab.
EduReport — Sistema de Gestión Escolar (MINERD República Dominicana)
"""

import os
from io import BytesIO
from datetime import date, datetime

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, KeepTogether, HRFlowable
)
from reportlab.pdfgen import canvas

from app.models.academic import CentroEducativo, Student, Section


class NumberedCanvas(canvas.Canvas):
    """Canvas de dos pasadas para calcular y mostrar el total de páginas (Página X de Y)."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_footer(num_pages)
            super().showPage()
        super().save()

    def draw_footer(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#64748b"))
        
        # Línea divisoria de pie de página
        self.setStrokeColor(colors.HexColor("#cbd5e1"))
        self.setLineWidth(0.5)
        self.line(36, 40, letter[0] - 36, 40)
        
        # Texto de pie de página
        footer_left = "EduReport — Sistema Oficial de Gestión y Reportes Escolares | MINERD"
        footer_right = f"Página {self._pageNumber} de {page_count}"
        self.drawString(36, 28, footer_left)
        self.drawRightString(letter[0] - 36, 28, footer_right)
        self.restoreState()


def get_default_institutional_data():
    """Obtiene los datos institucionales desde la BD o usa valores oficiales por defecto."""
    try:
        centro = CentroEducativo.query.first()
        if centro:
            return {
                'nombre': centro.nombre or 'Liceo Secundario República Dominicana',
                'regional': centro.regional or '10 - Santo Domingo',
                'distrito': centro.distrito or '01',
                'anio_escolar': centro.anio_escolar_activo or '2026-2027',
                'codigo_gestion': centro.codigo_gestion or '00124-MINERD',
                'telefono': centro.telefono or '(809) 555-0100',
                'direccion': centro.direccion or 'Av. Independencia #120, Santo Domingo',
            }
    except Exception:
        pass

    return {
        'nombre': 'Liceo Secundario República Dominicana',
        'regional': '10 - Santo Domingo',
        'distrito': '01',
        'anio_escolar': '2026-2027',
        'codigo_gestion': '00124-MINERD',
        'telefono': '(809) 555-0100',
        'direccion': 'Av. Independencia #120, Santo Domingo',
    }


def generate_official_pdf(data, output_stream=None):
    """
    Genera un informe oficial en PDF en formato profesional y listo para imprimir.
    
    Requisitos del documento:
    - Encabezado institucional
    - Nombre del centro
    - Logo oficial
    - Regional
    - Distrito
    - Año escolar
    - Datos del estudiante (nombre, RNE, grado, sección, tutor, teléfono)
    - Grado
    - Sección
    - Asignatura
    - Período
    - Fecha
    - Asunto
    - Situación
    - Análisis
    - Acciones
    - Recomendaciones
    - Conclusión
    - Espacios para firmas
    """
    if output_stream is None:
        buffer = BytesIO()
    else:
        buffer = output_stream

    # Configuración del documento: tamaño carta, márgenes estándar de 36 pt (0.5 pulgada)
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        leftMargin=36,
        rightMargin=36,
        topMargin=36,
        bottomMargin=54,
    )

    content_width = letter[0] - 72  # 612 - 72 = 540 pt

    # Estilos
    styles = getSampleStyleSheet()
    
    title_inst_style = ParagraphStyle(
        'InstTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10,
        leading=13,
        textColor=colors.HexColor('#1e3a8a'),
        alignment=1, # Centrado
    )
    
    subtitle_inst_style = ParagraphStyle(
        'InstSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8,
        leading=11,
        textColor=colors.HexColor('#334155'),
        alignment=1,
    )

    school_name_style = ParagraphStyle(
        'SchoolName',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=14,
        textColor=colors.HexColor('#0f172a'),
        alignment=1,
    )

    doc_title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=13,
        leading=16,
        textColor=colors.HexColor('#1e3a8a'),
        alignment=1,
    )

    section_header_style = ParagraphStyle(
        'SectionHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9.5,
        leading=12,
        textColor=colors.HexColor('#1e293b'),
    )

    body_style = ParagraphStyle(
        'DocBody',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        textColor=colors.HexColor('#1e293b'),
        alignment=4, # Justificado
    )

    meta_label_style = ParagraphStyle(
        'MetaLabel',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8.5,
        leading=11,
        textColor=colors.HexColor('#1e3a8a'),
    )

    meta_val_style = ParagraphStyle(
        'MetaVal',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=11,
        textColor=colors.HexColor('#0f172a'),
    )

    sign_title_style = ParagraphStyle(
        'SignTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8,
        leading=10,
        textColor=colors.HexColor('#0f172a'),
        alignment=1,
    )

    sign_sub_style = ParagraphStyle(
        'SignSub',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=7.5,
        leading=9.5,
        textColor=colors.HexColor('#475569'),
        alignment=1,
    )

    story = []

    # ─────────────────────────────────────────────────────────────────────────
    # 1. ENCABEZADO INSTITUCIONAL CON LOGO Y DATOS DE LA ESCUELA
    # ─────────────────────────────────────────────────────────────────────────
    inst = data.get('institucion', get_default_institutional_data())

    # Buscar logos oficiales usando rutas absolutas basadas en la ubicación de este archivo
    # Esto garantiza que funcionen en cualquier entorno (local, Render, Docker, etc.)
    _base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'static', 'img'))
    logo_minerd_path = os.path.join(_base_dir, 'logo_minerd.png')
    logo_centro_path = os.path.join(_base_dir, 'logo_centro.png')

    logo_minerd = None
    if os.path.exists(logo_minerd_path):
        try:
            logo_minerd = Image(logo_minerd_path, width=64, height=50)
        except Exception:
            logo_minerd = None

    logo_centro = None
    if os.path.exists(logo_centro_path):
        try:
            logo_centro = Image(logo_centro_path, width=50, height=50)
        except Exception:
            logo_centro = None

    header_text_cells = [
        Paragraph("REPÚBLICA DOMINICANA", title_inst_style),
        Paragraph("MINISTERIO DE EDUCACIÓN (MINERD)", title_inst_style),
        Paragraph("VICEMINISTERIO DE SERVICIOS TÉCNICOS Y PEDAGÓGICOS", subtitle_inst_style),
        Paragraph("DIRECCIÓN GENERAL DE EDUCACIÓN SECUNDARIA", subtitle_inst_style),
        Spacer(1, 2),
        Paragraph(inst.get('nombre', 'Liceo Secundario República Dominicana').upper(), school_name_style),
        Paragraph(
            f"Regional: <b>{inst.get('regional', '10')}</b> &bull; "
            f"Distrito: <b>{inst.get('distrito', '01')}</b> &bull; "
            f"Código de Gestión: <b>{inst.get('codigo_gestion', '00124-MINERD')}</b> &bull; "
            f"Año Escolar: <b>{inst.get('anio_escolar', '2026-2027')}</b>",
            subtitle_inst_style
        ),
    ]

    left_logo = logo_minerd or logo_centro
    right_logo = logo_centro or logo_minerd

    if left_logo and right_logo:
        header_table = Table(
            [[left_logo, header_text_cells, right_logo]],
            colWidths=[65, content_width - 130, 65]
        )
        header_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ALIGN', (0, 0), (0, -1), 'CENTER'),
            ('ALIGN', (2, 0), (2, -1), 'CENTER'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
            ('TOPPADDING', (0, 0), (-1, -1), 0),
        ]))
    elif left_logo:
        header_table = Table(
            [[left_logo, header_text_cells]],
            colWidths=[65, content_width - 65]
        )
        header_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
            ('TOPPADDING', (0, 0), (-1, -1), 0),
        ]))
    else:
        header_table = Table(
            [[header_text_cells]],
            colWidths=[content_width]
        )
        header_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ]))


    story.append(header_table)
    story.append(Spacer(1, 6))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#1e3a8a'), spaceAfter=8, spaceBefore=2))

    # ─────────────────────────────────────────────────────────────────────────
    # 2. TÍTULO Y ASUNTO DEL DOCUMENTO
    # ─────────────────────────────────────────────────────────────────────────
    asunto = data.get('asunto', 'INFORME PEDAGÓGICO Y DE SEGUIMIENTO').upper()
    story.append(Paragraph(asunto, doc_title_style))
    story.append(Spacer(1, 6))

    # ─────────────────────────────────────────────────────────────────────────
    # 3. METADATOS Y DATOS DEL ESTUDIANTE / GRADO / SECCIÓN / PERÍODO
    # ─────────────────────────────────────────────────────────────────────────
    fecha_str = data.get('fecha', date.today().strftime('%d/%m/%Y'))
    asignatura = data.get('asignatura', 'Todas las asignaturas / General')
    periodo = data.get('periodo', 'Todos los períodos (P1 - P4)')
    estudiante = data.get('estudiante', 'Estudiante no especificado')
    rne = data.get('rne', 'N/D')
    grado = data.get('grado', 'N/D')
    seccion = data.get('seccion', 'N/D')
    ciclo = data.get('ciclo', 'N/D')
    tutor = data.get('tutor', 'No registrado')
    telefono = data.get('telefono', 'Sin teléfono')

    meta_table_data = [
        [
            Paragraph("Fecha de Emisión:", meta_label_style),
            Paragraph(fecha_str, meta_val_style),
            Paragraph("Período:", meta_label_style),
            Paragraph(periodo, meta_val_style),
        ],
        [
            Paragraph("Asignatura:", meta_label_style),
            Paragraph(asignatura, meta_val_style),
            Paragraph("Año Escolar:", meta_label_style),
            Paragraph(inst.get('anio_escolar', '2026-2027'), meta_val_style),
        ],
        [
            Paragraph("Estudiante:", meta_label_style),
            Paragraph(f"<b>{estudiante}</b>", meta_val_style),
            Paragraph("RNE / Matrícula:", meta_label_style),
            Paragraph(f"<b>{rne}</b>", meta_val_style),
        ],
        [
            Paragraph("Grado y Sección:", meta_label_style),
            Paragraph(f"{grado} — Sección {seccion}", meta_val_style),
            Paragraph("Ciclo:", meta_label_style),
            Paragraph(ciclo, meta_val_style),
        ],
        [
            Paragraph("Familiar / Tutor:", meta_label_style),
            Paragraph(tutor, meta_val_style),
            Paragraph("Teléfono Tutor:", meta_label_style),
            Paragraph(telefono, meta_val_style),
        ],
    ]

    col_w = [90, (content_width / 2) - 90, 85, (content_width / 2) - 85]
    meta_table = Table(meta_table_data, colWidths=col_w)
    meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f8fafc')),
        ('BOX', (0, 0), (-1, -1), 0.75, colors.HexColor('#cbd5e1')),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
    ]))

    story.append(meta_table)
    story.append(Spacer(1, 10))

    # ─────────────────────────────────────────────────────────────────────────
    # 4. SECCIONES TEMÁTICAS REQUERIDAS:
    #    - SITUACIÓN
    #    - ANÁLISIS
    #    - ACCIONES
    #    - RECOMENDACIONES
    #    - CONCLUSIÓN
    # ─────────────────────────────────────────────────────────────────────────
    sections_def = [
        ("I. SITUACIÓN OBSERVADA", data.get('situacion', 'No se ha registrado una descripción de la situación observada.')),
        ("II. ANÁLISIS PEDAGÓGICO Y DE DATOS", data.get('analisis', 'No se ha registrado un análisis preliminar.')),
        ("III. ACCIONES IMPLEMENTADAS Y ACORDADAS", data.get('acciones', 'No se han registrado acciones acordadas a la fecha.')),
        ("IV. RECOMENDACIONES", data.get('recomendaciones', 'Continuar con el seguimiento rutinario conforme a las directrices pedagógicas.')),
        ("V. CONCLUSIÓN", data.get('conclusion', 'Se da constancia del presente informe para su archivo y seguimiento en el expediente escolar.')),
    ]

    for title, text in sections_def:
        # Título de sección con barra de fondo azul suave
        sec_header = Table(
            [[Paragraph(f"<b>{title}</b>", section_header_style)]],
            colWidths=[content_width]
        )
        sec_header.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#e0e7ff')),
            ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor('#c7d2fe')),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ]))

        story.append(sec_header)
        story.append(Spacer(1, 3))

        # Párrafos de contenido
        lines = text.strip().split('\n')
        for line in lines:
            line_clean = line.strip()
            if not line_clean:
                story.append(Spacer(1, 3))
                continue
            story.append(Paragraph(line_clean, body_style))
        story.append(Spacer(1, 7))

    # ─────────────────────────────────────────────────────────────────────────
    # 5. ESPACIOS PARA FIRMAS OFICIALES (4 FIRMAS: Docente, Orientación, Dirección, Tutor)
    # ─────────────────────────────────────────────────────────────────────────
    story.append(Spacer(1, 10))
    signatures_title = Paragraph("<b>CONSTANCIA Y FIRMAS DE RESPONSABILIDAD INSTITUCIONAL</b>", ParagraphStyle(
        'SignBlockTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8.5,
        textColor=colors.HexColor('#334155'),
        alignment=1,
    ))
    story.append(signatures_title)
    story.append(Spacer(1, 14))

    col_sign_w = (content_width - 24) / 4
    signatures_data = [
        [
            Paragraph("____________________________<br/><b>Docente / Tutor de Aula</b><br/><font color='#64748b'>Firma y Sello</font>", sign_title_style),
            Paragraph("____________________________<br/><b>Orientación y Psicología</b><br/><font color='#64748b'>Firma y Sello</font>", sign_title_style),
            Paragraph("____________________________<br/><b>Dirección del Centro</b><br/><font color='#64748b'>Firma y Sello Oficial</font>", sign_title_style),
            Paragraph("____________________________<br/><b>Padre / Madre / Tutor Legal</b><br/><font color='#64748b'>Firma del Familiar</font>", sign_title_style),
        ]
    ]

    signatures_table = Table(signatures_data, colWidths=[col_sign_w, col_sign_w, col_sign_w, col_sign_w])
    signatures_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 2),
        ('RIGHTPADDING', (0, 0), (-1, -1), 2),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))

    story.append(KeepTogether([signatures_table]))

    # Construir PDF con NumberedCanvas
    doc.build(story, canvasmaker=NumberedCanvas)

    if output_stream is None:
        buffer.seek(0)
        return buffer.getvalue()
    return buffer


def build_report_data_from_student(tipo_reporte, student, asignatura=None, periodo='P1', observaciones_docente=''):
    """
    Construye la estructura de datos requerida para el PDF con datos reales del estudiante,
    asistencia, rendimiento y directrices del MINERD.
    """
    from app.services import attendance_service, evaluation_service

    inst_data = get_default_institutional_data()
    today_str = date.today().strftime('%d/%m/%Y')

    student_name = student.full_name if student else "General"
    rne = student.registration_number if student else "N/D"
    section_name = student.section.nombre if (student and student.section) else (student.section.name if student and student.section else "N/D")
    grade_name = student.section.grade_level.name if (student and student.section and student.section.grade_level) else "N/D"
    grado_name = grade_name
    cycle_name = student.section.grade_level.cycle.name if (student and student.section and student.section.grade_level and student.section.grade_level.cycle) else "N/D"
    tutor_name = student.tutor_name if student and student.tutor_name else "Padre, Madre o Tutor no registrado"
    tutor_phone = student.tutor_phone if student and student.tutor_phone else "Sin teléfono"

    asig_nombre = asignatura.nombre if asignatura else "Todas las asignaturas"

    # Obtener resúmenes
    att_summary = attendance_service.get_student_attendance_summary(student.id) if student else {}
    acad_summary = evaluation_service.get_student_academic_summary(student.id) if student else {}

    # Generar secciones de contenido basadas en el tipo de reporte
    if 'Asistencia' in tipo_reporte:
        ausencias_count = att_summary.get('ausentes', 0)
        tardanzas_count = att_summary.get('tardanzas', 0)
        presentes_count = att_summary.get('presentes', 0)
        porcentaje = att_summary.get('porcentaje', 0.0)

        situacion = (
            f"El/la estudiante {student_name}, perteneciente a la sección {section_name}, "
            f"ha registrado a la fecha un acumulado de {ausencias_count} ausencia(s) injustificada(s) "
            f"y {tardanzas_count} tardanza(s), con {presentes_count} asistencias efectivas en el período evaluado."
        )

        if ausencias_count >= 3:
            situacion += (
                f"\n\nATENCIÓN: Se ha activado la ALERTA OFICIAL de EduReport al alcanzar o superar el umbral "
                f"de 3 ausencias acumuladas, requiriendo intervención inmediata según el protocolo escolar."
            )

        analisis = (
            f"El porcentaje de asistencia global del estudiante se sitúa en un {porcentaje}%. "
            f"La acumulación de ausencias impacta de manera directa en el proceso continuo de enseñanza-aprendizaje, "
            f"limitando la participación en las actividades pedagógicas y la evaluación formativa de competencias."
        )

        acciones = (
            "1. Notificación formal y oportuna al padre, madre o tutor legal del estudiante.\n"
            "2. Citación a entrevista presencial para conocer las causas de las ausencias.\n"
            "3. Firma de un acta de compromiso de asistencia regular.\n"
            "4. Remisión del caso al Departamento de Orientación y Psicología Escolar."
        )

        recomendaciones = (
            "1. Garantizar la puntualidad y asistencia diaria a la jornada escolar.\n"
            "2. Presentar oportunamente las justificaciones médicas o causas de fuerza mayor ante la secretaría docente.\n"
            "3. Mantener comunicación constante entre la familia y el centro educativo."
        )

        conclusion = (
            "Se emite el presente informe para formalizar el seguimiento de asistencia del estudiante, "
            "dejando constancia en su expediente acumulativo y coordinando las medidas preventivas necesarias "
            "para salvaguardar su permanencia y éxito escolar."
        )

    elif 'Bajo Rendimiento' in tipo_reporte:
        promedio = acad_summary.get('promedio_general', 0.0)
        bajas = [a for a in acad_summary.get('por_asignatura', []) if not a.get('aprobada', True)]
        nombres_bajas = ", ".join([f"{a['asignatura'].nombre} ({a['promedio']} pts)" for a in bajas]) or "Ninguna identificada con promedio reprobatorio"

        situacion = (
            f"El/la estudiante {student_name} presenta un promedio general de {promedio} puntos en el período lectivo, "
            f"situándose por debajo del estándar mínimo aprobatorio de 70 puntos establecido en el currículo nacional.\n"
            f"Asignaturas que demandan atención prioritaria: {nombres_bajas}."
        )

        analisis = (
            f"Se constata dificultad en el logro de los indicadores de aprendizaje previstos para el grado {grado_name}. "
            f"El rendimiento académico refleja la necesidad de aplicar estrategias diferenciadas de nivelación pedagógica "
            f"y refuerzo en las competencias específicas fundamentales."
        )

        acciones = (
            "1. Inscripción inmediata en el programa de Recuperación Pedagógica (RP).\n"
            "2. Entrega de guías de trabajo y actividades de refuerzo guiadas.\n"
            "3. Reunión informativa con los familiares para coordinar el apoyo académico en el hogar."
        )

        recomendaciones = (
            "1. Establecer un horario de estudio diario en el hogar de al menos 2 horas.\n"
            "2. Asistir a las sesiones de tutoría y recuperación pedagógica organizadas por el liceo.\n"
            "3. Consultar oportunamente a los docentes ante dudas o dificultades en los contenidos temáticos."
        )

        conclusion = (
            "El centro educativo pone a disposición todos los recursos pedagógicos de acompañamiento "
            "para que el/la estudiante supere las dificultades detectadas y alcance las competencias requeridas."
        )

    else:
        # Avance Académico / Progreso / Integral
        promedio = acad_summary.get('promedio_general', 70.0)
        situacion = (
            f"El/la estudiante {student_name} cursa el grado {grado_name}, sección {section_name}, "
            f"en el ciclo {cycle_name}. Durante el período {periodo}, se ha llevado a cabo el seguimiento sistemático "
            f"de sus evaluaciones formativas y sumativas en concordancia con el diseño curricular del MINERD."
        )

        analisis = (
            f"El promedio académico general alcanzado se sitúa en {promedio} puntos. "
            f"Se evidencia el desarrollo de competencias fundamentales conforme a los indicadores de logro trabajados. "
            f"El registro de asistencia muestra un {att_summary.get('porcentaje', 100)}% de días efectivos."
        )

        acciones = (
            "1. Monitoreo pedagógico continuo en todas las áreas del conocimiento.\n"
            "2. Retroalimentación constructiva en los períodos de evaluación bimestral.\n"
            "3. Coordinación interdisciplinar entre el equipo docente y de orientación."
        )

        recomendaciones = (
            "1. Mantener la constancia y el compromiso en la entrega de asignaciones y proyectos escolares.\n"
            "2. Fortalecer los hábitos de lectura y pensamiento analítico.\n"
            "3. Fomentar la participación activa en los talleres y actividades complementarias del centro."
        )

        conclusion = (
            "Se certifica que el estudiante continúa avanzando en su trayectoria educativa regular, "
            "cumpliendo satisfactoriamente con los requerimientos establecidos para su nivel escolar."
        )

    if observaciones_docente:
        situacion += f"\n\nObservaciones adicionales del docente:\n{observaciones_docente}"

    return {
        'institucion': inst_data,
        'fecha': today_str,
        'asunto': tipo_reporte,
        'asignatura': asig_nombre,
        'periodo': periodo,
        'estudiante': student_name,
        'rne': rne,
        'grado': grade_name,
        'seccion': section_name,
        'ciclo': cycle_name,
        'tutor': tutor_name,
        'telefono': tutor_phone,
        'situacion': situacion,
        'analisis': analisis,
        'acciones': acciones,
        'recomendaciones': recomendaciones,
        'conclusion': conclusion,
    }

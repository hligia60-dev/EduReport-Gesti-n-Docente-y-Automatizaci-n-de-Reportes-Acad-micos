import os
import zipfile
import xml.etree.ElementTree as ET
from datetime import date, timedelta
from app import db
from app.models.academic import CentroEducativo, Aula, Estudiante, Familiar, Cycle, GradeLevel
from app.models.attendance import Asistencia
from app.models.evaluation import (
    Asignatura,
    CompetenciaFundamental,
    CompetenciaEspecifica,
    IndicadorLogro,
    ContenidoCurricular,
    Evaluacion,
    Seguimiento,
    Reporte
)

def parse_docx_roster(filepath):
    """Extrae la lista de estudiantes desde un archivo DOCX oficial del registro escolar."""
    if not os.path.exists(filepath):
        return []

    try:
        with zipfile.ZipFile(filepath) as z:
            xml_content = z.read('word/document.xml')
            tree = ET.fromstring(xml_content)
            ns = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
            
            rows = tree.findall('.//w:tr', ns)
            students = []
            for r in rows:
                cells = r.findall('.//w:tc', ns)
                row_data = []
                for c in cells:
                    texts = [node.text for node in c.iter() if node.tag.endswith('t') and node.text]
                    cell_text = "".join(texts).strip()
                    row_data.append(cell_text)
                
                # Descartar encabezados o filas vacías
                if not row_data or len(row_data) < 4:
                    continue
                if row_data[0].lower().startswith('no'):
                    continue
                if not row_data[0].isdigit():
                    continue
                    
                num_orden = int(row_data[0])
                nombre_raw = row_data[1]
                fecha_nac = row_data[2] if len(row_data) > 2 else ''
                tel = row_data[3] if len(row_data) > 3 else ''
                sexo = row_data[4] if len(row_data) > 4 else ''
                
                # Normalizar sexo
                sexo = sexo.strip().upper()
                if sexo not in ('M', 'F'):
                    sexo = 'F' if 'F' in sexo else 'M'
                    
                # Separar nombres y apellidos (normativa MINERD: Apellidos primero)
                parts = nombre_raw.split()
                if len(parts) >= 4:
                    apellidos = " ".join(parts[:2])
                    nombres = " ".join(parts[2:])
                elif len(parts) == 3:
                    apellidos = " ".join(parts[:2])
                    nombres = parts[2]
                elif len(parts) == 2:
                    apellidos = parts[0]
                    nombres = parts[1]
                else:
                    apellidos = nombre_raw
                    nombres = nombre_raw

                students.append({
                    'num_orden': num_orden,
                    'nombre_completo': nombre_raw,
                    'nombres': nombres.title(),
                    'apellidos': apellidos.title(),
                    'fecha_nacimiento': fecha_nac,
                    'telefono': tel,
                    'sexo': sexo
                })
            return students
    except Exception as e:
        print(f"Error al analizar {filepath}: {e}")
        return []


def seed_database_if_empty():
    """
    Inicializa la base de datos con la estructura curricular completa del MINERD,
    los 13 modelos relacionales y los datos reales extraídos de los documentos:
    - 2DO B 2026-2027.docx
    - 3ERO B 2026-2027.docx
    - 6TO A (ANTIGUO 4TO.) 2026-2027.docx
    """
    if CentroEducativo.query.first():
        return  # La base de datos ya contiene datos

    print("Inicializando base de datos EduReport con los 13 modelos y datos de los registros oficiales...")

    # 1. Centro Educativo (MINERD)
    centro = CentroEducativo(
        nombre='Liceo Secundario República Dominicana',
        codigo_gestion='00124-MINERD',
        codigo_sigerd='SIG-2026-8841',
        codigo_cartografia='CART-10-01-2026',
        regional='10 - Santo Domingo',
        distrito='01',
        director='Prof. Ramón Altagracia',
        director_telefono='(809) 555-0101',
        director_correo='director.liceo@minerd.gob.do',
        telefono='(809) 555-0100',
        correo='liceo.secundaria@minerd.gob.do',
        direccion='Av. Independencia #120, Santo Domingo',
        sector='Público',
        zona='Urbana',
        jornada='Jornada Escolar Extendida (JEE)',
        anio_escolar_activo='2026-2027'
    )
    db.session.add(centro)
    db.session.flush()

    # 2. Ciclos del Nivel Secundario
    c1 = Cycle(name='Primer Ciclo', description='1.º, 2.º y 3.º de Secundaria (Modalidad General)')
    c2 = Cycle(name='Segundo Ciclo', description='4.º, 5.º y 6.º de Secundaria (Modalidad Académica / Técnica)')
    db.session.add_all([c1, c2])
    db.session.flush()

    # 3. Grados Académicos (1.º a 6.º de Secundaria)
    g1 = GradeLevel(name='1.º de Secundaria', order=1, cycle_id=c1.id)
    g2 = GradeLevel(name='2.º de Secundaria', order=2, cycle_id=c1.id)
    g3 = GradeLevel(name='3.º de Secundaria', order=3, cycle_id=c1.id)
    g4 = GradeLevel(name='4.º de Secundaria', order=4, cycle_id=c2.id)
    g5 = GradeLevel(name='5.º de Secundaria', order=5, cycle_id=c2.id)
    g6 = GradeLevel(name='6.º de Secundaria', order=6, cycle_id=c2.id)
    grades_map = {1: g1, 2: g2, 3: g3, 4: g4, 5: g5, 6: g6}
    db.session.add_all(list(grades_map.values()))
    db.session.flush()

    # 4. Aulas / Cursos Escolares
    # Cursos específicos de los documentos suministrados:
    aula_2b = Aula(
        centro_id=centro.id,
        grade_id=g2.id,
        nombre='2DO B',
        name='B',
        grado='2.º de Secundaria',
        seccion='B',
        ciclo='Primer Ciclo',
        modalidad='General',
        school_year='2026-2027',
        docente_titular='Prof. Marcos Peña',
        capacidad_maxima=40
    )
    aula_3b = Aula(
        centro_id=centro.id,
        grade_id=g3.id,
        nombre='3RO B',
        name='B',
        grado='3.º de Secundaria',
        seccion='B',
        ciclo='Primer Ciclo',
        modalidad='General',
        school_year='2026-2027',
        docente_titular='Prof. Carmen Rosario',
        capacidad_maxima=40
    )
    aula_6a = Aula(
        centro_id=centro.id,
        grade_id=g6.id,
        nombre='6TO A',
        name='A',
        grado='6.º de Secundaria',
        seccion='A',
        ciclo='Segundo Ciclo',
        modalidad='Académica',
        school_year='2026-2027',
        docente_titular='Prof. Laura Fernández',
        capacidad_maxima=40
    )

    # Aulas complementarias para tener cobertura completa en todos los grados
    aulas_extra = [
        Aula(centro_id=centro.id, grade_id=g1.id, nombre='1RO A', name='A', grado='1.º de Secundaria', seccion='A', ciclo='Primer Ciclo', school_year='2026-2027'),
        Aula(centro_id=centro.id, grade_id=g1.id, nombre='1RO B', name='B', grado='1.º de Secundaria', seccion='B', ciclo='Primer Ciclo', school_year='2026-2027'),
        Aula(centro_id=centro.id, grade_id=g2.id, nombre='2DO A', name='A', grado='2.º de Secundaria', seccion='A', ciclo='Primer Ciclo', school_year='2026-2027'),
        Aula(centro_id=centro.id, grade_id=g3.id, nombre='3RO A', name='A', grado='3.º de Secundaria', seccion='A', ciclo='Primer Ciclo', school_year='2026-2027'),
        Aula(centro_id=centro.id, grade_id=g4.id, nombre='4TO A', name='A', grado='4.º de Secundaria', seccion='A', ciclo='Segundo Ciclo', school_year='2026-2027'),
        Aula(centro_id=centro.id, grade_id=g4.id, nombre='4TO B', name='B', grado='4.º de Secundaria', seccion='B', ciclo='Segundo Ciclo', school_year='2026-2027'),
        Aula(centro_id=centro.id, grade_id=g5.id, nombre='5TO A', name='A', grado='5.º de Secundaria', seccion='A', ciclo='Segundo Ciclo', school_year='2026-2027'),
        Aula(centro_id=centro.id, grade_id=g5.id, nombre='5TO B', name='B', grado='5.º de Secundaria', seccion='B', ciclo='Segundo Ciclo', school_year='2026-2027'),
        Aula(centro_id=centro.id, grade_id=g6.id, nombre='6TO B', name='B', grado='6.º de Secundaria', seccion='B', ciclo='Segundo Ciclo', school_year='2026-2027'),
    ]

    all_aulas = [aula_2b, aula_3b, aula_6a] + aulas_extra
    db.session.add_all(all_aulas)
    db.session.flush()

    # 5. Competencias Fundamentales del MINERD (7 Competencias)
    cf_data = [
        ('CF-COM', 'Comunicativa', 'Desarrolla la capacidad de comunicarse de forma oral, escrita y simbólica con precisión y respeto en diversos contextos socioculturales.'),
        ('CF-PLC', 'Pensamiento Lógico, Creativo y Crítico', 'Construye conclusiones basadas en razonamientos estructurados, genera ideas innovadoras y analiza críticamente la realidad.'),
        ('CF-RP',  'Resolución de Problemas', 'Identifica, analiza y resuelve situaciones problemáticas cotidianas y complejas aplicando estrategias sistemáticas.'),
        ('CF-CT',  'Científica y Tecnológica', 'Explica fenómenos naturales y sociales aplicando el método científico y herramientas tecnológicas de vanguardia.'),
        ('CF-AS',  'Ambiental y de la Salud', 'Promueve el cuidado responsable del medio ambiente, la salud física y comunitaria para un desarrollo sostenible.'),
        ('CF-DPE', 'Desarrollo Personal y Espiritual', 'Fomenta el autoconocimiento, la autoestima, la resiliencia y el sentido ético y espiritual de la vida.'),
        ('CF-EC',  'Ética y Ciudadana', 'Participa activamente en la construcción de una sociedad democrática, justa, inclusiva y pacífica.')
    ]
    cf_objs = []
    cf_dict = {}
    for codigo, nombre, desc in cf_data:
        cf = CompetenciaFundamental(codigo=codigo, nombre=nombre, descripcion=desc)
        cf_objs.append(cf)
    db.session.add_all(cf_objs)
    db.session.flush()
    for cf in cf_objs:
        cf_dict[cf.codigo] = cf

    # 6. Asignaturas del Plan de Estudio
    asig_data = [
        ('ESP',  'Lengua Española', 'Humanidades y Lenguas', 'Ambos', 5, False),
        ('ING',  'Lenguas Extranjeras - Inglés', 'Humanidades y Lenguas', 'Ambos', 4, False),
        ('FRA',  'Lenguas Extranjeras - Francés', 'Humanidades y Lenguas', 'Ambos', 3, False),
        ('MAT',  'Matemática', 'Ciencias Exactas', 'Ambos', 5, False),
        ('SOC',  'Ciencias Sociales', 'Ciencias Sociales', 'Ambos', 4, False),
        ('NAT',  'Ciencias de la Naturaleza', 'Ciencias Naturales', 'Ambos', 4, False),
        ('ART',  'Educación Artística', 'Artes y Expresión', 'Ambos', 2, False),
        ('EFI',  'Educación Física', 'Salud y Movimiento', 'Ambos', 2, False),
        ('FIHR', 'Formación Integral Humana y Religiosa', 'Valores y Espiritualidad', 'Ambos', 2, False),
        ('OPT',  'Salida Optativa (Tecnología / Humanidades)', 'Optativa Especializada', 'Segundo Ciclo', 4, True)
    ]
    asig_objs = []
    asig_dict = {}
    for cod, nom, area, cic, hrs, opt in asig_data:
        asig = Asignatura(codigo=cod, nombre=nom, area=area, ciclo=cic, horas_semanales=hrs, es_optativa=opt)
        asig_objs.append(asig)
    db.session.add_all(asig_objs)
    db.session.flush()
    for a in asig_objs:
        asig_dict[a.codigo] = a

    # 7. Competencias Específicas e Indicadores de Logro
    ce_esp = CompetenciaEspecifica(
        asignatura_id=asig_dict['ESP'].id,
        competencia_fundamental_id=cf_dict['CF-COM'].id,
        grade_id=g2.id,
        codigo='CE-LE1',
        name='Comprensión y Producción Escrita de Textos Funcionales',
        type='Específica',
        descripcion='Comprende y produce textos orales y escritos formales utilizando las estructuras sintácticas y gramaticales normativas.'
    )
    ce_mat = CompetenciaEspecifica(
        asignatura_id=asig_dict['MAT'].id,
        competencia_fundamental_id=cf_dict['CF-RP'].id,
        grade_id=g2.id,
        codigo='CE-MAT1',
        name='Resolución de Problemas con Ecuaciones y Modelado',
        type='Específica',
        descripcion='Aplica modelos algebraicos y geométricos para resolver problemas del entorno y la comunidad.'
    )
    ce_nat = CompetenciaEspecifica(
        asignatura_id=asig_dict['NAT'].id,
        competencia_fundamental_id=cf_dict['CF-CT'].id,
        grade_id=g6.id,
        codigo='CE-NAT1',
        name='Investigación Científica y Fenómenos Físicos',
        type='Específica',
        descripcion='Analiza fenómenos mecánicos, cinemáticos y termodinámicos mediante el método científico experimental.'
    )
    db.session.add_all([ce_esp, ce_mat, ce_nat])
    db.session.flush()

    # Indicadores de Logro
    il1 = IndicadorLogro(competency_id=ce_esp.id, code='IL-LE1.1', description='Escribe informes de investigación con claridad, coherencia y adecuación léxica.', period='P1')
    il2 = IndicadorLogro(competency_id=ce_esp.id, code='IL-LE1.2', description='Identifica ideas principales y secundarias en textos argumentativos y científicos.', period='P2')
    il3 = IndicadorLogro(competency_id=ce_mat.id, code='IL-MAT1.1', description='Resuelve sistemas de ecuaciones lineales aplicados a situaciones económicas cotidianas.', period='P1')
    il4 = IndicadorLogro(competency_id=ce_nat.id, code='IL-NAT1.1', description='Aplica las leyes de Newton en experimentos prácticos de laboratorio.', period='P1')
    db.session.add_all([il1, il2, il3, il4])
    db.session.flush()

    # 8. Contenidos Curriculares por Período
    cc1 = ContenidoCurricular(asignatura_id=asig_dict['ESP'].id, competencia_especifica_id=ce_esp.id, periodo='P1', tema='El Informe de Lectura y Ensayo Argumentativo', tipo='Conceptual', descripcion='Estructura, conectores de causa y consecuencia, normas de citación.')
    cc2 = ContenidoCurricular(asignatura_id=asig_dict['MAT'].id, competencia_especifica_id=ce_mat.id, periodo='P1', tema='Sistemas de Ecuaciones Lineales', tipo='Procedimental', descripcion='Métodos de igualación, sustitución, reducción y método gráfico.')
    cc3 = ContenidoCurricular(asignatura_id=asig_dict['NAT'].id, competencia_especifica_id=ce_nat.id, periodo='P1', tema='Cinemática y Dinámica de Cuerpos', tipo='Conceptual', descripcion='Velocidad, aceleración, fuerzas fundamentales y leyes del movimiento.')
    db.session.add_all([cc1, cc2, cc3])
    db.session.flush()

    # 9. Cargar Estudiantes Reales desde los 3 Documentos DOCX
    def find_roster_file(pattern):
        search_dirs = [
            'base de datos de estudiantes',
            '.',
            os.path.abspath('base de datos de estudiantes'),
            os.path.abspath('.'),
            os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'base de datos de estudiantes')),
            os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
        ]
        for d in search_dirs:
            if os.path.exists(d):
                for fname in os.listdir(d):
                    if pattern.lower() in fname.lower() and fname.endswith('.docx'):
                        return os.path.join(d, fname)
        return None

    doc_paths = [
        (find_roster_file('2DO B'), aula_2b, '2B'),
        (find_roster_file('3ERO B') or find_roster_file('3RO B'), aula_3b, '3B'),
        (find_roster_file('6TO A'), aula_6a, '6A')
    ]

    total_estudiantes_cargados = 0
    all_inserted_students = []

    for path, aula_obj, code_prefix in doc_paths:
        if not path:
            continue
        roster = parse_docx_roster(path)
        for row in roster:
            num = row['num_orden']
            rne = f"RNE-2026-{code_prefix}-{num:02d}"
            
            # Crear Estudiante
            estudiante = Estudiante(
                section_id=aula_obj.id,
                numero_orden=num,
                registration_number=rne,
                first_name=row['nombres'],
                last_name=row['apellidos'],
                gender=row['sexo'],
                birth_date=row['fecha_nacimiento'],
                condicion_inicial='Promovido',
                tutor_name=f"Tutor de {row['nombres']} {row['apellidos']}",
                tutor_phone='(000)000-0000',
                tutor_relationship='Padre/Madre/Tutor',
                is_active=True
            )
            db.session.add(estudiante)
            db.session.flush()
            all_inserted_students.append(estudiante)

            # Crear Familiar correspondiente con su número de WhatsApp/Teléfono
            familiar = Familiar(
                estudiante_id=estudiante.id,
                nombres=f"Tutor de {estudiante.first_name} {estudiante.last_name}",
                parentesco='Madre' if num % 2 == 0 else 'Padre',
                telefono='(000)000-0000',
                whatsapp='(000)000-0000',
                es_contacto_principal=True,
                es_contacto_emergencia=True
            )
            db.session.add(familiar)
            total_estudiantes_cargados += 1

    print(f"Cargados exitosamente {total_estudiantes_cargados} estudiantes y sus familiares desde los registros oficiales.")

    # 10. Asistencias Históricas y Demostración de la Regla de 3 Ausencias
    today = date.today()
    
    # Tomar estudiantes muestra para aplicar alertas y asistencias normales
    if all_inserted_students:
        # Estudiante 1 (2DO B): Con 3 ausencias acumuladas (Alerta Activa)
        s_alerta_1 = all_inserted_students[0]
        att_alert_1 = [
            Asistencia(student_id=s_alerta_1.id, aula_id=s_alerta_1.section_id, asignatura_id=asig_dict['ESP'].id, date=today - timedelta(days=7), status='Ausente', codigo_estado='A', notes='Falta sin justificación reportada'),
            Asistencia(student_id=s_alerta_1.id, aula_id=s_alerta_1.section_id, asignatura_id=asig_dict['MAT'].id, date=today - timedelta(days=4), status='Ausente', codigo_estado='A', notes='No se presentó a clases'),
            Asistencia(student_id=s_alerta_1.id, aula_id=s_alerta_1.section_id, asignatura_id=asig_dict['SOC'].id, date=today - timedelta(days=1), status='Ausente', codigo_estado='A', notes='3.ª falta acumulada - Alerta activada'),
            Asistencia(student_id=s_alerta_1.id, aula_id=s_alerta_1.section_id, asignatura_id=asig_dict['NAT'].id, date=today - timedelta(days=9), status='Presente', codigo_estado='P', notes='Puntual')
        ]
        db.session.add_all(att_alert_1)

        # Seguimiento Oficial para el Estudiante 1 (Regla de 3 Ausencias)
        seg_1 = Seguimiento(
            student_id=s_alerta_1.id,
            aula_id=s_alerta_1.section_id,
            fecha=today,
            tipo='Alerta 3 Ausencias',
            motivo='Acumulación de 3 inasistencias en el mes escolar',
            descripcion='El sistema detectó automáticamente la 3.ª inasistencia consecutiva/alternada. Se requiere citación formal con el departamento de orientación.',
            acciones_acordadas='Se emitió la circular de citación para firma del tutor y compromiso pedagógico de recuperación.',
            status='En Proceso',
            responsable='Departamento de Orientación y Psicología'
        )
        db.session.add(seg_1)

        # Reporte Oficial generado para el Estudiante 1
        rep_1 = Reporte(
            tipo_reporte='Ficha de Seguimiento de Asistencia',
            estudiante_id=s_alerta_1.id,
            aula_id=s_alerta_1.section_id,
            periodo='P1',
            titulo=f"Ficha de Citación por 3 Ausencias - {s_alerta_1.full_name}",
            generado_por='Sistema EduReport (Automático)'
        )
        db.session.add(rep_1)

        # Estudiante en 3ERO B con 3 ausencias (Alerta Activa en 3ero)
        estudiantes_3b = [s for s in all_inserted_students if s.section_id == aula_3b.id]
        if estudiantes_3b:
            s_alerta_2 = estudiantes_3b[0]
            att_alert_2 = [
                Asistencia(student_id=s_alerta_2.id, aula_id=aula_3b.id, date=today - timedelta(days=6), status='Ausente', codigo_estado='A', notes='Falta injustificada'),
                Asistencia(student_id=s_alerta_2.id, aula_id=aula_3b.id, date=today - timedelta(days=3), status='Ausente', codigo_estado='A', notes='Segunda falta'),
                Asistencia(student_id=s_alerta_2.id, aula_id=aula_3b.id, date=today - timedelta(days=1), status='Ausente', codigo_estado='A', notes='3.ª falta acumulada')
            ]
            db.session.add_all(att_alert_2)

        # Asistencias regulares para el resto de estudiantes
        for idx, s in enumerate(all_inserted_students[1:25]):
            status = 'Presente' if idx % 5 != 0 else ('Tardanza' if idx % 2 == 0 else 'Excusa')
            code = 'P' if status == 'Presente' else ('T' if status == 'Tardanza' else 'E')
            att = Asistencia(
                student_id=s.id,
                aula_id=s.section_id,
                date=today - timedelta(days=idx % 3),
                status=status,
                codigo_estado=code,
                notes='Registro regular de asistencia'
            )
            db.session.add(att)

        # 11. Evaluaciones de Aprendizaje (P1 a P4)
        for s in all_inserted_students[:10]:
            eval_p1 = Evaluacion(
                student_id=s.id,
                asignatura_id=asig_dict['ESP'].id,
                indicator_id=il1.id,
                period='P1',
                score=85.0 if s.id % 2 == 0 else 74.0,
                calificacion_final_periodo=85.0 if s.id % 2 == 0 else 74.0,
                tipo='Ordinaria',
                aprobado=True
            )
            eval_p2 = Evaluacion(
                student_id=s.id,
                asignatura_id=asig_dict['MAT'].id,
                indicator_id=il3.id,
                period='P1',
                score=90.0 if s.id % 2 == 0 else 68.0,
                calificacion_recuperacion=72.0 if s.id % 2 != 0 else None,
                calificacion_final_periodo=90.0 if s.id % 2 == 0 else 72.0,
                tipo='Ordinaria' if s.id % 2 == 0 else 'Recuperacion',
                aprobado=True
            )
            db.session.add_all([eval_p1, eval_p2])

    db.session.commit()
    print("¡Base de datos EduReport inicializada y poblada exitosamente con todos los modelos y datos oficiales!")

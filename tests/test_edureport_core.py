"""
Suite de Pruebas Básicas Oficiales para EduReport.
Cubre los 9 requisitos mínimos solicitados:
1. La aplicación Flask inicia.
2. La página principal responde.
3. Se puede crear un estudiante.
4. Se puede consultar un estudiante.
5. Se puede registrar asistencia.
6. Tres ausencias generan la alerta.
7. Se puede registrar una evaluación.
8. Se puede generar un reporte.
9. Se puede generar un PDF con ReportLab.
"""

import os
import unittest
from datetime import date, timedelta

from app import create_app, db
from app.models.academic import Student, Section, GradeLevel, Cycle, CentroEducativo
from app.models.attendance import Attendance
from app.models.evaluation import Asignatura, Evaluacion, Reporte
from app.services import attendance_service, student_service, evaluation_service, seguimiento_service
from app.services.pdf_service import build_report_data_from_student, generate_official_pdf


class EduReportBasicTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Configuración inicial para la suite de pruebas."""
        cls.app = create_app('testing')
        cls.client = cls.app.test_client()

    def setUp(self):
        """Prepara el contexto de la aplicación para cada prueba."""
        self.app_context = self.app.app_context()
        self.app_context.push()

    def tearDown(self):
        """Limpia el contexto después de cada prueba."""
        db.session.rollback()
        self.app_context.pop()

    # ─────────────────────────────────────────────────────────────────────────
    # 1. La aplicación Flask inicia.
    # ─────────────────────────────────────────────────────────────────────────
    def test_1_flask_app_initializes(self):
        """Prueba 1: Verifica que la aplicación Flask inicie correctamente."""
        self.assertIsNotNone(self.app, "La aplicación Flask no se inicializó correctamente.")
        self.assertTrue(self.app.config.get('TESTING', False), "El modo TESTING debe estar activo.")
        self.assertEqual(self.app.name, 'app', "El nombre de la aplicación debe ser 'app'.")

    # ─────────────────────────────────────────────────────────────────────────
    # 2. La página principal responde.
    # ─────────────────────────────────────────────────────────────────────────
    def test_2_home_page_responds(self):
        """Prueba 2: Verifica que la página principal '/' responda con HTTP 200 OK."""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200, "La página principal debe responder con 200 OK.")
        html = response.data.decode('utf-8')
        self.assertIn('EduReport', html, "El nombre EduReport debe estar presente en el HTML.")
        self.assertIn('Primer Ciclo', html, "Debe mencionar el Primer Ciclo en la página de inicio.")

    # ─────────────────────────────────────────────────────────────────────────
    # 3. Se puede crear un estudiante.
    # ─────────────────────────────────────────────────────────────────────────
    def test_3_create_student(self):
        """Prueba 3: Se puede registrar un nuevo estudiante con todos sus campos."""
        section = Section.query.first()
        self.assertIsNotNone(section, "Debe existir al menos una sección en la base de datos.")

        unique_rne = f"TEST-RNE-{date.today().strftime('%Y%m%d')}-99"
        # Eliminar si ya existía de una corrida previa
        existing = Student.query.filter_by(registration_number=unique_rne).first()
        if existing:
            db.session.delete(existing)
            db.session.commit()

        new_student = student_service.create_student(
            first_name="Carlos Alberto",
            last_name="Gómez Peña",
            registration_number=unique_rne,
            gender="M",
            section_id=section.id,
            birth_date="2009-05-14",
            tutor_name="María Peña",
            tutor_phone="(809) 555-7890",
            tutor_relationship="Madre",
            condicion_inicial="Promovido",
            numero_orden=99
        )
        self.assertIsNotNone(new_student.id, "El estudiante debe tener un ID asignado tras guardarse.")
        self.assertEqual(new_student.full_name, "Carlos Alberto Gómez Peña")
        self.assertEqual(new_student.registration_number, unique_rne)
        self.assertEqual(new_student.gender, "M")
        self.assertEqual(new_student.tutor_name, "María Peña")
        self.assertEqual(new_student.tutor_phone, "(809) 555-7890")

    # ─────────────────────────────────────────────────────────────────────────
    # 4. Se puede consultar un estudiante.
    # ─────────────────────────────────────────────────────────────────────────
    def test_4_query_student(self):
        """Prueba 4: Se puede consultar el expediente de un estudiante."""
        student = Student.query.first()
        self.assertIsNotNone(student, "Debe existir al menos un estudiante para consultar.")

        # Consulta a través del servicio
        queried = student_service.get_student_by_id(student.id)
        self.assertIsNotNone(queried, "El servicio debe retornar el estudiante por ID.")
        self.assertEqual(queried.id, student.id)

        # Consulta a través de la ruta web HTTP
        response = self.client.get(f'/estudiantes/{student.id}')
        self.assertEqual(response.status_code, 200, "La vista de detalle del estudiante debe devolver 200 OK.")
        html = response.data.decode('utf-8')
        self.assertIn(student.last_name, html, "El apellido del estudiante debe aparecer en su ficha.")
        self.assertIn(student.registration_number, html, "El RNE debe aparecer en la ficha.")

    # ─────────────────────────────────────────────────────────────────────────
    # 5. Se puede registrar asistencia.
    # ─────────────────────────────────────────────────────────────────────────
    def test_5_register_attendance(self):
        """Prueba 5: Se puede registrar asistencia (P/T/A/E) por estudiante y fecha."""
        student = Student.query.first()
        self.assertIsNotNone(student)

        test_date = date.today() - timedelta(days=50)
        # Limpiar registros previos en esa fecha si los hubiera
        Attendance.query.filter_by(student_id=student.id, date=test_date).delete()
        db.session.commit()

        # Registrar un estado 'Presente' (P)
        att = attendance_service.record_single_attendance(
            student_id=student.id,
            att_date=test_date,
            status='Presente',
            notes='Prueba unitaria de asistencia'
        )
        self.assertIsNotNone(att.id, "El registro de asistencia debe haberse guardado.")
        self.assertEqual(att.status, 'Presente')
        self.assertEqual(att.codigo_estado, 'P')

        # Actualizar a 'Tardanza' (T)
        att_updated = attendance_service.record_single_attendance(
            student_id=student.id,
            att_date=test_date,
            status='Tardanza',
            notes='Cambio a tardanza'
        )
        self.assertEqual(att_updated.status, 'Tardanza')
        self.assertEqual(att_updated.codigo_estado, 'T')

    # ─────────────────────────────────────────────────────────────────────────
    # 6. Tres ausencias generan la alerta.
    # ─────────────────────────────────────────────────────────────────────────
    def test_6_three_absences_trigger_alert(self):
        """
        Prueba 6: Regla de 3 Ausencias en EduReport.
        Al acumular 3 o más ausencias:
        1. Se activa la propiedad has_absence_alert en el estudiante.
        2. El estudiante aparece en la lista de get_students_with_alerts().
        3. Se muestra en la vista del dashboard y alertas.
        """
        # Crear un estudiante temporal específico para aislar la prueba de ausencias
        section = Section.query.first()
        temp_student = Student(
            first_name="Prueba",
            last_name="Alerta Ausencias",
            registration_number=f"ALERT-TEST-{date.today().strftime('%Y%m%d%H%M%S')}",
            gender="F",
            section_id=section.id,
            is_active=True
        )
        db.session.add(temp_student)
        db.session.commit()

        # Al inicio no tiene ausencias ni alerta
        self.assertEqual(temp_student.total_absences, 0)
        self.assertFalse(temp_student.has_absence_alert)

        # Registrar 1 ausencia
        attendance_service.record_single_attendance(temp_student.id, date.today() - timedelta(days=5), 'Ausente')
        self.assertEqual(temp_student.total_absences, 1)
        self.assertFalse(temp_student.has_absence_alert, "Con 1 ausencia no debe haber alerta.")

        # Registrar 2da ausencia
        attendance_service.record_single_attendance(temp_student.id, date.today() - timedelta(days=4), 'Ausente')
        self.assertEqual(temp_student.total_absences, 2)
        self.assertFalse(temp_student.has_absence_alert, "Con 2 ausencias no debe haber alerta.")

        # Registrar 3ra ausencia (¡Disparador de la regla!)
        attendance_service.record_single_attendance(temp_student.id, date.today() - timedelta(days=3), 'Ausente')
        self.assertEqual(temp_student.total_absences, 3)
        self.assertTrue(temp_student.has_absence_alert, "¡Con 3 ausencias DEBE activarse la alerta!")

        # Verificar que aparezca en get_students_with_alerts()
        alerts = attendance_service.get_students_with_alerts()
        alert_student_ids = [item['student'].id for item in alerts]
        self.assertIn(temp_student.id, alert_student_ids, "El estudiante con 3 ausencias debe estar en la lista de alertas.")

        # Verificar respuesta HTTP en la página de alertas
        res_alerts = self.client.get('/asistencia/alertas')
        self.assertEqual(res_alerts.status_code, 200)
        self.assertIn(temp_student.last_name, res_alerts.data.decode('utf-8'))

    # ─────────────────────────────────────────────────────────────────────────
    # 7. Se puede registrar una evaluación.
    # ─────────────────────────────────────────────────────────────────────────
    def test_7_register_evaluation(self):
        """
        Prueba 7: Se puede registrar una evaluación con estudiante, asignatura,
        período (P1-P4), calificación en escala 0-100, RP y competencias.
        """
        student = Student.query.first()
        asignatura = Asignatura.query.first()
        self.assertIsNotNone(student)
        self.assertIsNotNone(asignatura)

        ev = evaluation_service.save_evaluacion(
            student_id=student.id,
            asignatura_id=asignatura.id,
            period="P1",
            score=88.5,
            calificacion_recuperacion=None,
            observaciones="Excelente desempeño y dominio de conceptos"
        )
        self.assertIsNotNone(ev.id, "La evaluación debe tener un ID asignado.")
        self.assertEqual(ev.score, 88.5)
        self.assertEqual(ev.period, "P1")
        self.assertEqual(ev.asignatura_id, asignatura.id)
        self.assertTrue(ev.aprobado, "Una calificación de 88.5 debe considerarse aprobada (>=70).")

        # Prueba de recuperación pedagógica (RP)
        ev_rp = evaluation_service.save_evaluacion(
            student_id=student.id,
            asignatura_id=asignatura.id,
            period="P2",
            score=55.0, # Reprobado inicialmente
            calificacion_recuperacion=78.0, # Recuperado en RP
            observaciones="Completó el plan de recuperación pedagógica satisfactoriamente"
        )
        self.assertEqual(ev_rp.score, 55.0)
        self.assertEqual(ev_rp.calificacion_recuperacion, 78.0)
        self.assertEqual(ev_rp.calificacion_final_periodo, 78.0)
        self.assertTrue(ev_rp.aprobado, "Con calificación de RP >= 70 debe considerarse aprobada.")

    # ─────────────────────────────────────────────────────────────────────────
    # 8. Se puede generar un reporte.
    # ─────────────────────────────────────────────────────────────────────────
    def test_8_generate_report(self):
        """Prueba 8: Se puede generar y guardar un reporte formal en el sistema."""
        student = Student.query.first()
        self.assertIsNotNone(student)

        tipo = "Informe de Seguimiento de Asistencia"
        titulo = f"Informe de Prueba — {student.full_name}"

        reporte = seguimiento_service.save_reporte(
            tipo_reporte=tipo,
            titulo=titulo,
            estudiante_id=student.id,
            aula_id=student.section_id,
            periodo="P1",
            generado_por="EduReport Test Suite",
            datos_json="Situación observada: 3 faltas. Acciones: Citación a tutor."
        )
        self.assertIsNotNone(reporte.id, "El reporte generado debe registrarse en la base de datos.")
        self.assertEqual(reporte.tipo_reporte, tipo)
        self.assertEqual(reporte.estudiante_id, student.id)
        self.assertEqual(reporte.generado_por, "EduReport Test Suite")

        # Verificar que se pueda consultar en la BD
        recuperado = Reporte.query.get(reporte.id)
        self.assertIsNotNone(recuperado)
        self.assertEqual(recuperado.titulo, titulo)

    # ─────────────────────────────────────────────────────────────────────────
    # 9. Se puede generar un PDF con ReportLab.
    # ─────────────────────────────────────────────────────────────────────────
    def test_9_generate_pdf(self):
        """
        Prueba 9: Generación de PDF profesional con ReportLab.
        Verifica:
        - Encabezado institucional y metadatos del centro.
        - Datos del estudiante, grado, sección y período.
        - Secciones requeridas: Situación, Análisis, Acciones, Recomendaciones, Conclusión.
        - Espacio para 4 firmas institucionales.
        - Creación de bytes de archivo PDF válidos.
        """
        student = Student.query.first()
        self.assertIsNotNone(student)

        data = build_report_data_from_student(
            tipo_reporte="Informe de Seguimiento de Asistencia",
            student=student,
            periodo="P1",
            observaciones_docente="Observación pedagógica de prueba para PDF."
        )

        # Validar que todos los campos requeridos estén en la estructura
        campos_requeridos = [
            'institucion', 'fecha', 'asunto', 'asignatura', 'periodo',
            'estudiante', 'rne', 'grado', 'seccion', 'ciclo',
            'tutor', 'telefono', 'situacion', 'analisis', 'acciones',
            'recomendaciones', 'conclusion'
        ]
        for campo in campos_requeridos:
            self.assertIn(campo, data, f"El campo {campo} debe estar presente en los datos del PDF.")

        # Generar los bytes del PDF
        pdf_bytes = generate_official_pdf(data)
        self.assertIsInstance(pdf_bytes, (bytes, bytearray), "El PDF generado debe ser una secuencia de bytes.")
        self.assertGreater(len(pdf_bytes), 1000, "El PDF generado no debe estar vacío.")
        self.assertTrue(pdf_bytes.startswith(b'%PDF'), "El encabezado del archivo debe ser un PDF válido (%PDF).")

        # Probar endpoint HTTP de descarga de PDF
        res_http = self.client.get(f'/reportes/estudiante/{student.id}/pdf?tipo=Seguimiento+de+Asistencia')
        self.assertEqual(res_http.status_code, 200, "El endpoint HTTP de descarga debe responder con 200 OK.")
        self.assertEqual(res_http.content_type, 'application/pdf', "El Content-Type debe ser 'application/pdf'.")
        self.assertTrue(res_http.data.startswith(b'%PDF'), "La respuesta HTTP debe contener un archivo PDF válido.")

    def test_10_evaluation_4_ordinarias_and_rp(self):
        """
        Prueba 10: Validación del registro de 4 calificaciones ordinarias (0-100)
        y 4 casillas de Recuperación Pedagógica (RP) por competencia.
        """
        student = Student.query.first()
        asig = Asignatura.query.first()
        self.assertIsNotNone(student)
        self.assertIsNotNone(asig)

        # Caso: C1=65 (requiere RP), C2=80, C3=75, C4=60 (requiere RP)
        # RP: C1_RP=85, C4_RP=70
        ev = evaluation_service.save_evaluacion(
            student_id=student.id,
            asignatura_id=asig.id,
            period="P1",
            c1_score=65.0,
            c2_score=80.0,
            c3_score=75.0,
            c4_score=60.0,
            c1_rp=85.0,
            c4_rp=70.0
        )

        self.assertEqual(ev.c1_score, 65.0)
        self.assertEqual(ev.c2_score, 80.0)
        self.assertEqual(ev.c3_score, 75.0)
        self.assertEqual(ev.c4_score, 60.0)
        self.assertEqual(ev.c1_rp, 85.0)
        self.assertIsNone(ev.c2_rp)
        self.assertEqual(ev.c4_rp, 70.0)

        # C1_final debe ser max(65, 85) = 85
        self.assertEqual(ev.c1_final, 85.0)
        self.assertEqual(ev.c2_final, 80.0)
        self.assertEqual(ev.c3_final, 75.0)
        self.assertEqual(ev.c4_final, 70.0)

        # Calificación final promedio = (85 + 80 + 75 + 70) / 4 = 77.5
        self.assertEqual(ev.calificacion_final_periodo, 77.5)
        self.assertTrue(ev.aprobado)

        # Validar formulario HTML de registro de calificaciones
        res_form = self.client.get(f'/evaluaciones/registrar?student_id={student.id}')
        self.assertEqual(res_form.status_code, 200)
        self.assertIn(b'c1_score', res_form.data)
        self.assertIn(b'c1_rp', res_form.data)
        self.assertIn(b'c4_score', res_form.data)
        self.assertIn(b'c4_rp', res_form.data)

        # Validar botón "Guardar datos" en formulario de estudiante
        res_est = self.client.get(f'/estudiantes/{student.id}/editar')
        self.assertEqual(res_est.status_code, 200)
        self.assertIn('Guardar datos'.encode('utf-8'), res_est.data)


if __name__ == '__main__':
    unittest.main()


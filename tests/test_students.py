import pytest
from app import create_app, db
from app.models.academic import Student, Section, GradeLevel, Cycle, Familiar

@pytest.fixture
def app():
    app = create_app('testing')
    return app

@pytest.fixture
def client(app):
    return app.test_client()

def test_list_students(client):
    """Prueba listar estudiantes (GET /estudiantes/)."""
    res = client.get('/estudiantes/')
    assert res.status_code == 200
    html = res.data.decode('utf-8')
    assert 'Gestión de Estudiantes' in html
    assert 'Primer Ciclo' in html
    assert 'Segundo Ciclo' in html

def test_search_students(client):
    """Prueba buscar estudiantes por nombre, apellido y RNE."""
    # Búsqueda por RNE
    res = client.get('/estudiantes/?q=2B-01')
    assert res.status_code == 200
    html = res.data.decode('utf-8')
    assert 'RNE-2026-2B-01' in html

    # Búsqueda por apellido
    res2 = client.get('/estudiantes/?q=Adon')
    assert res2.status_code == 200
    html2 = res2.data.decode('utf-8')
    assert 'Adon' in html2

def test_filter_students_by_cycle_and_grade(client):
    """Prueba filtrar estudiantes por Primer y Segundo Ciclo."""
    # Filtrar por Primer Ciclo
    with client.application.app_context():
        c1 = Cycle.query.filter_by(name='Primer Ciclo').first()
        c2 = Cycle.query.filter_by(name='Segundo Ciclo').first()
        c1_id = c1.id
        c2_id = c2.id

    res_c1 = client.get(f'/estudiantes/?cycle_id={c1_id}')
    assert res_c1.status_code == 200
    html_c1 = res_c1.data.decode('utf-8')
    assert 'Primer Ciclo' in html_c1

    res_c2 = client.get(f'/estudiantes/?cycle_id={c2_id}')
    assert res_c2.status_code == 200
    html_c2 = res_c2.data.decode('utf-8')
    assert 'Segundo Ciclo' in html_c2

def test_consultar_estudiante_detail(client):
    """Prueba consultar la ficha individual de un estudiante (GET /estudiantes/<id>)."""
    with client.application.app_context():
        s = Student.query.first()
        s_id = s.id
        rne = s.registration_number
        name = s.first_name

    res = client.get(f'/estudiantes/{s_id}')
    assert res.status_code == 200
    html = res.data.decode('utf-8')
    assert rne in html
    assert name in html
    assert 'Familiar y Contacto de Emergencia' in html
    assert 'Información Curricular y Escolar' in html

def test_agregar_estudiante_primer_ciclo(client):
    """Prueba agregar un nuevo estudiante en el Primer Ciclo (1.º a 3.º)."""
    with client.application.app_context():
        sec_2b = Section.query.filter_by(nombre='2DO B').first()
        sec_id = sec_2b.id

    post_data = {
        'first_name': 'Ramón Alberto',
        'last_name': 'Santana Morales',
        'registration_number': 'RNE-2026-TEST-01',
        'gender': 'M',
        'section_id': sec_id,
        'birth_date': '14/05/2012',
        'condicion_inicial': 'Promovido',
        'tutor_name': 'Julia Morales',
        'tutor_phone': '809-555-1234',
        'tutor_relationship': 'Madre',
        'numero_orden': '41'
    }

    res = client.post('/estudiantes/nuevo', data=post_data, follow_redirects=True)
    assert res.status_code == 200
    html = res.data.decode('utf-8')
    assert 'Ramón Alberto' in html
    assert 'Santana Morales' in html
    assert 'RNE-2026-TEST-01' in html

    # Verificar en base de datos
    with client.application.app_context():
        est = Student.query.filter_by(registration_number='RNE-2026-TEST-01').first()
        assert est is not None
        assert est.first_name == 'Ramón Alberto'
        assert est.section.grade_level.cycle.name == 'Primer Ciclo'
        assert est.condicion_inicial == 'Promovido'
        assert len(est.familiares) > 0
        assert est.familiares[0].telefono == '809-555-1234'

def test_agregar_estudiante_segundo_ciclo(client):
    """Prueba agregar un nuevo estudiante en el Segundo Ciclo (4.º a 6.º)."""
    with client.application.app_context():
        sec_6a = Section.query.filter_by(nombre='6TO A').first()
        sec_id = sec_6a.id

    post_data = {
        'first_name': 'Camila Nicole',
        'last_name': 'Taveras Cruz',
        'registration_number': 'RNE-2026-TEST-02',
        'gender': 'F',
        'section_id': sec_id,
        'birth_date': '20/09/2009',
        'condicion_inicial': 'Promovido',
        'tutor_name': 'Pedro Taveras',
        'tutor_phone': '829-555-9876',
        'tutor_relationship': 'Padre',
        'numero_orden': '40'
    }

    res = client.post('/estudiantes/nuevo', data=post_data, follow_redirects=True)
    assert res.status_code == 200
    html = res.data.decode('utf-8')
    assert 'Camila Nicole' in html

    # Verificar en base de datos
    with client.application.app_context():
        est = Student.query.filter_by(registration_number='RNE-2026-TEST-02').first()
        assert est is not None
        assert est.section.grade_level.cycle.name == 'Segundo Ciclo'

def test_editar_estudiante(client):
    """Prueba editar los datos de un estudiante existente."""
    with client.application.app_context():
        est = Student.query.first()
        est_id = est.id
        sec_id = est.section_id

    update_data = {
        'first_name': 'Nombre Modificado',
        'last_name': 'Apellido Modificado',
        'registration_number': 'RNE-EDIT-001',
        'gender': 'F',
        'section_id': sec_id,
        'birth_date': '15/08/2012',
        'condicion_inicial': 'Repitente',
        'tutor_name': 'Tutor Actualizado',
        'tutor_phone': '809-555-9999',
        'tutor_relationship': 'Madre',
        'numero_orden': '1'
    }

    res = client.post(f'/estudiantes/{est_id}/editar', data=update_data, follow_redirects=True)
    assert res.status_code == 200
    html = res.data.decode('utf-8')
    assert 'Nombre Modificado' in html
    assert 'Repitente' in html

    with client.application.app_context():
        est_updated = db.session.get(Student, est_id)
        assert est_updated.first_name == 'Nombre Modificado'
        assert est_updated.condicion_inicial == 'Repitente'
        assert est_updated.familiares[0].telefono == '809-555-9999'

def test_eliminar_estudiante(client):
    """Prueba eliminar un estudiante."""
    with client.application.app_context():
        # Crear un estudiante temporal para eliminar
        sec = Section.query.first()
        est_temp = Student(
            first_name='Para',
            last_name='Eliminar',
            registration_number='RNE-PARA-ELIMINAR',
            section_id=sec.id
        )
        db.session.add(est_temp)
        db.session.commit()
        temp_id = est_temp.id

    res = client.post(f'/estudiantes/{temp_id}/eliminar', follow_redirects=True)
    assert res.status_code == 200
    html = res.data.decode('utf-8')
    assert 'ha sido eliminado exitosamente' in html

    with client.application.app_context():
        est_deleted = db.session.get(Student, temp_id)
        assert est_deleted is None

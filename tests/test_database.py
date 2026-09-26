import pytest
from app import create_app, db
from app.models import (
    CentroEducativo,
    Aula,
    Estudiante,
    Familiar,
    Asistencia,
    Asignatura,
    CompetenciaFundamental,
    CompetenciaEspecifica,
    IndicadorLogro,
    ContenidoCurricular,
    Evaluacion,
    Seguimiento,
    Reporte
)

@pytest.fixture
def app():
    app = create_app('testing')
    return app

def test_all_13_tables_created(app):
    """Verifica que las 13 tablas requeridas se creen en la base de datos."""
    with app.app_context():
        inspector = db.inspect(db.engine)
        tables = inspector.get_table_names()
        
        required_tables = [
            'centros_educativos',
            'aulas',
            'estudiantes',
            'familiares',
            'asistencias',
            'asignaturas',
            'competencias_fundamentales',
            'competencias_especificas',
            'indicadores_logro',
            'contenidos_curriculares',
            'evaluaciones',
            'seguimientos',
            'reportes'
        ]
        
        for table in required_tables:
            assert table in tables, f"La tabla {table} no existe en la base de datos."

def test_centro_educativo_exists(app):
    """Verifica que exista el registro institucional del Centro Educativo."""
    with app.app_context():
        centro = CentroEducativo.query.first()
        assert centro is not None
        assert centro.nombre is not None
        assert len(centro.aulas) > 0

def test_docx_rosters_loaded(app):
    """Verifica que los cursos 2DO B, 3RO B y 6TO A tengan sus estudiantes matriculados."""
    with app.app_context():
        aula_2b = Aula.query.filter_by(nombre='2DO B').first()
        aula_3b = Aula.query.filter_by(nombre='3RO B').first()
        aula_6a = Aula.query.filter_by(nombre='6TO A').first()
        
        assert aula_2b is not None, "Aula 2DO B no encontrada"
        assert aula_3b is not None, "Aula 3RO B no encontrada"
        assert aula_6a is not None, "Aula 6TO A no encontrada"
        
        assert len(aula_2b.estudiantes) == 40, f"Se esperaban 40 estudiantes en 2DO B, se encontraron {len(aula_2b.estudiantes)}"
        assert len(aula_3b.estudiantes) == 37, f"Se esperaban 37 estudiantes en 3RO B, se encontraron {len(aula_3b.estudiantes)}"
        assert len(aula_6a.estudiantes) == 39, f"Se esperaban 39 estudiantes en 6TO A, se encontraron {len(aula_6a.estudiantes)}"

def test_estudiante_familiar_relationship(app):
    """Verifica que cada estudiante tenga su contacto familiar con teléfono/WhatsApp."""
    with app.app_context():
        estudiante = Estudiante.query.first()
        assert estudiante is not None
        assert len(estudiante.familiares) > 0
        familiar = estudiante.familiares[0]
        assert familiar.nombres is not None
        assert familiar.telefono is not None

def test_curriculum_and_evaluation_models(app):
    """Verifica las asignaturas, competencias, contenidos y evaluaciones."""
    with app.app_context():
        assert CompetenciaFundamental.query.count() == 7
        assert Asignatura.query.count() >= 9
        assert CompetenciaEspecifica.query.count() > 0
        assert IndicadorLogro.query.count() > 0
        assert ContenidoCurricular.query.count() > 0
        assert Evaluacion.query.count() > 0
        assert Seguimiento.query.count() > 0
        assert Reporte.query.count() > 0

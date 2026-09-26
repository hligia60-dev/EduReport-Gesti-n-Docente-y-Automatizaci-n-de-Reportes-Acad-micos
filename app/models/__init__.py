# Paquete de modelos de datos (SQLAlchemy ORM) - EduReport
from app.models.academic import (
    CentroEducativo,
    Aula,
    Estudiante,
    Familiar,
    Cycle,
    GradeLevel,
    Section,
    Student
)
from app.models.attendance import (
    Asistencia,
    Attendance
)
from app.models.evaluation import (
    Asignatura,
    CompetenciaFundamental,
    CompetenciaEspecifica,
    IndicadorLogro,
    ContenidoCurricular,
    Evaluacion,
    Seguimiento,
    Reporte,
    Competency,
    Indicator,
    Grade,
    PedagogicalRecovery
)

__all__ = [
    # 13 Modelos Oficiales Requeridos
    'CentroEducativo',
    'Aula',
    'Estudiante',
    'Familiar',
    'Asistencia',
    'Asignatura',
    'CompetenciaFundamental',
    'CompetenciaEspecifica',
    'IndicadorLogro',
    'ContenidoCurricular',
    'Evaluacion',
    'Seguimiento',
    'Reporte',
    # Compatibilidad y Estructura Curricular
    'Cycle',
    'GradeLevel',
    'Section',
    'Student',
    'Attendance',
    'Competency',
    'Indicator',
    'Grade',
    'PedagogicalRecovery'
]

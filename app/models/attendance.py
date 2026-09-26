from datetime import datetime, date
from app import db

class Asistencia(db.Model):
    """
    Modelo para el registro de asistencia diaria de estudiantes.
    Soporta los estados normativos del MINERD:
    P = Presente
    A = Ausencia
    T = Tardanza (3 tardanzas = 1 ausencia)
    E = Excusa justificada (enfermedad, defunción de familiar, etc.)
    R = Retiro voluntario
    """
    __tablename__ = 'asistencias'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('estudiantes.id'), nullable=False)
    aula_id = db.Column(db.Integer, db.ForeignKey('aulas.id'), nullable=True)
    asignatura_id = db.Column(db.Integer, db.ForeignKey('asignaturas.id'), nullable=True)
    date = db.Column(db.Date, default=date.today, nullable=False)
    status = db.Column(db.String(20), nullable=False, default='Presente') # 'Presente', 'Ausente', 'Tardanza', 'Excusa', 'Retirado'
    codigo_estado = db.Column(db.String(5), nullable=True, default='P')   # 'P', 'A', 'T', 'E', 'R'
    notes = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Restricción única opcional por estudiante y fecha
    __table_args__ = (
        db.UniqueConstraint('student_id', 'date', 'asignatura_id', name='uq_student_date_subject_attendance'),
    )

    # Propiedades y sinónimos para compatibilidad
    @property
    def estudiante_id(self):
        return self.student_id

    @property
    def fecha(self):
        return self.date

    @property
    def estado(self):
        return self.status

    @property
    def observaciones(self):
        return self.notes

    def __repr__(self):
        return f'<Asistencia Estudiante:{self.student_id} Fecha:{self.date} Estado:{self.status} ({self.codigo_estado})>'


# Alias de compatibilidad
Attendance = Asistencia

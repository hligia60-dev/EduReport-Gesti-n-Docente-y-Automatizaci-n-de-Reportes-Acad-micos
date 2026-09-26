from datetime import datetime
from app import db

class Cycle(db.Model):
    """Modelo para los Ciclos del Nivel Secundario (Primer Ciclo, Segundo Ciclo)."""
    __tablename__ = 'cycles'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False, unique=True)
    description = db.Column(db.String(255), nullable=True)

    # Relación con Grados
    grades = db.relationship('GradeLevel', backref='cycle', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Cycle {self.name}>'


class GradeLevel(db.Model):
    """Modelo para Grados Académicos (1.º a 6.º de Secundaria)."""
    __tablename__ = 'grade_levels'

    id = db.Column(db.Integer, primary_key=True)
    cycle_id = db.Column(db.Integer, db.ForeignKey('cycles.id'), nullable=False)
    name = db.Column(db.String(50), nullable=False)  # Ej: "2.º de Secundaria"
    order = db.Column(db.Integer, nullable=False)    # 1 a 6

    # Relaciones con Aulas/Secciones y Competencias
    aulas = db.relationship('Aula', backref='grade_level', lazy=True, cascade='all, delete-orphan')
    competencias = db.relationship('CompetenciaEspecifica', backref='grade_level', lazy=True)

    @property
    def sections(self):
        return self.aulas

    def __repr__(self):
        return f'<GradeLevel {self.name}>'


class CentroEducativo(db.Model):
    """
    Modelo para el Centro Educativo (MINERD - República Dominicana).
    Centraliza datos institucionales, códigos oficiales de gestión y localización.
    """
    __tablename__ = 'centros_educativos'

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(150), nullable=False, default='Liceo Secundario República Dominicana')
    codigo_gestion = db.Column(db.String(50), nullable=True, default='00124-MINERD')
    codigo_sigerd = db.Column(db.String(50), nullable=True, default='SIG-2026-8841')
    codigo_cartografia = db.Column(db.String(50), nullable=True, default='CART-10-01-2026')
    regional = db.Column(db.String(50), nullable=True, default='10 - Santo Domingo')
    distrito = db.Column(db.String(50), nullable=True, default='01')
    director = db.Column(db.String(120), nullable=True, default='Prof. Ramón Altagracia')
    director_telefono = db.Column(db.String(30), nullable=True, default='(809) 555-0101')
    director_correo = db.Column(db.String(120), nullable=True, default='director@minerd.gob.do')
    telefono = db.Column(db.String(30), nullable=True, default='(809) 555-0100')
    correo = db.Column(db.String(120), nullable=True, default='centro.secundaria@minerd.gob.do')
    direccion = db.Column(db.String(255), nullable=True, default='Av. Independencia #120, Santo Domingo')
    sector = db.Column(db.String(30), default='Público') # Público / Privado / Semioficial
    zona = db.Column(db.String(50), default='Urbana')    # Urbana / Rural
    jornada = db.Column(db.String(50), default='Jornada Escolar Extendida (JEE)')
    anio_escolar_activo = db.Column(db.String(20), default='2026-2027')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relación con Aulas
    aulas = db.relationship('Aula', backref='centro_educativo', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<CentroEducativo {self.nombre} ({self.codigo_gestion})>'


class Aula(db.Model):
    """
    Modelo para Aulas / Secciones Escolares.
    Representa el curso escolar (ej. '2DO B', '3RO B', '6TO A') con su grado, sección y ciclo.
    """
    __tablename__ = 'aulas'

    id = db.Column(db.Integer, primary_key=True)
    centro_id = db.Column(db.Integer, db.ForeignKey('centros_educativos.id'), nullable=True)
    grade_id = db.Column(db.Integer, db.ForeignKey('grade_levels.id'), nullable=True)
    
    # Identificadores y Nomenclatura Oficial
    nombre = db.Column(db.String(50), nullable=True)           # Ej: "2DO B", "3RO B", "6TO A"
    name = db.Column(db.String(20), nullable=False, default='A')# Ej: "B", "A" (compatibilidad de sección)
    grado = db.Column(db.String(50), nullable=True)            # Ej: "2.º de Secundaria"
    seccion = db.Column(db.String(10), nullable=True)          # Ej: "B", "A"
    ciclo = db.Column(db.String(50), nullable=True)            # Ej: "Primer Ciclo", "Segundo Ciclo"
    modalidad = db.Column(db.String(50), default='Académica')  # Ej: "General", "Académica", "Técnica"
    school_year = db.Column(db.String(20), default='2026-2027')# Año Lectivo Oficial
    docente_titular = db.Column(db.String(120), nullable=True) # Nombre del docente encargado
    docente_telefono = db.Column(db.String(30), nullable=True)
    docente_correo = db.Column(db.String(120), nullable=True)
    capacidad_maxima = db.Column(db.Integer, default=40)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.nombre and self.name:
            self.nombre = self.name
        if not self.seccion and self.name:
            self.seccion = self.name

    # Relaciones
    estudiantes = db.relationship('Estudiante', backref='aula', lazy=True, cascade='all, delete-orphan')
    asistencias = db.relationship('Asistencia', backref='aula', lazy=True, cascade='all, delete-orphan')
    seguimientos = db.relationship('Seguimiento', backref='aula', lazy=True, cascade='all, delete-orphan')
    reportes = db.relationship('Reporte', backref='aula', lazy=True, cascade='all, delete-orphan')

    # Propiedades de compatibilidad con el modelo anterior Section
    @property
    def students(self):
        return self.estudiantes

    @property
    def anio_escolar(self):
        return self.school_year

    @property
    def full_name(self):
        grado_str = self.grado or (self.grade_level.name if self.grade_level else self.nombre)
        return f"{grado_str} - Sección {self.name}"

    def __repr__(self):
        return f'<Aula {self.nombre} ({self.school_year})>'


class Estudiante(db.Model):
    """
    Modelo para Estudiantes del Nivel Secundario.
    Contiene la ficha integral del estudiante: RNE, orden, condición y datos personales.
    """
    __tablename__ = 'estudiantes'

    id = db.Column(db.Integer, primary_key=True)
    section_id = db.Column(db.Integer, db.ForeignKey('aulas.id'), nullable=False)
    numero_orden = db.Column(db.Integer, nullable=True)          # No. de orden en el registro (1 a 40)
    registration_number = db.Column(db.String(30), unique=True, nullable=False) # RNE oficial
    first_name = db.Column(db.String(100), nullable=False)       # Nombres
    last_name = db.Column(db.String(100), nullable=False)        # Apellidos
    gender = db.Column(db.String(10), nullable=True)             # 'F' o 'M'
    birth_date = db.Column(db.String(20), nullable=True)         # Fecha de nacimiento (DD/MM/AAAA)
    cedula_pasaporte = db.Column(db.String(30), nullable=True)
    lugar_nacimiento = db.Column(db.String(120), nullable=True)
    libro_nacimiento = db.Column(db.String(20), nullable=True)
    folio_nacimiento = db.Column(db.String(20), nullable=True)
    condicion_inicial = db.Column(db.String(30), default='Promovido') # Promovido, Repitente, Reingreso, Aplazado
    direccion = db.Column(db.String(200), nullable=True)
    correo = db.Column(db.String(100), nullable=True)
    
    # Tutor principal / Datos de contacto directo
    tutor_name = db.Column(db.String(120), nullable=True)
    tutor_phone = db.Column(db.String(30), nullable=True)
    tutor_relationship = db.Column(db.String(50), default='Padre/Madre/Tutor')
    
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relaciones
    familiares = db.relationship('Familiar', backref='estudiante', lazy=True, cascade='all, delete-orphan')
    asistencias = db.relationship('Asistencia', backref='estudiante', lazy=True, cascade='all, delete-orphan')
    evaluaciones = db.relationship('Evaluacion', backref='estudiante', lazy=True, cascade='all, delete-orphan')
    seguimientos = db.relationship('Seguimiento', backref='estudiante', lazy=True, cascade='all, delete-orphan')
    reportes = db.relationship('Reporte', backref='estudiante', lazy=True, cascade='all, delete-orphan')

    # Propiedades y sinónimos para compatibilidad en español e inglés
    @property
    def aula_id(self):
        return self.section_id

    @property
    def section(self):
        return self.aula

    @property
    def rne(self):
        return self.registration_number

    @property
    def nombres(self):
        return self.first_name

    @property
    def apellidos(self):
        return self.last_name

    @property
    def sexo(self):
        return self.gender

    @property
    def fecha_nacimiento(self):
        return self.birth_date

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()

    @property
    def nombre_completo(self):
        return self.full_name

    @property
    def attendances(self):
        return self.asistencias

    @property
    def grades(self):
        return self.evaluaciones

    @property
    def total_absences(self):
        """Calcula el total de ausencias acumuladas."""
        return sum(1 for a in self.asistencias if a.status in ('Ausente', 'A'))

    @property
    def total_ausencias(self):
        return self.total_absences

    @property
    def has_absence_alert(self):
        """Regla de Negocio EduReport: Al acumular 3 ausencias se activa la alerta."""
        return self.total_absences >= 3

    @property
    def tiene_alerta_ausencias(self):
        return self.has_absence_alert

    def __repr__(self):
        return f'<Estudiante {self.registration_number} - {self.full_name}>'


class Familiar(db.Model):
    """
    Modelo para Familiares y Contactos de Emergencia del Estudiante.
    Almacena datos de padres, madres, tutores legales y teléfonos de WhatsApp/emergencia.
    """
    __tablename__ = 'familiares'

    id = db.Column(db.Integer, primary_key=True)
    estudiante_id = db.Column(db.Integer, db.ForeignKey('estudiantes.id'), nullable=False)
    nombres = db.Column(db.String(120), nullable=False)
    parentesco = db.Column(db.String(50), nullable=False, default='Tutor Legal') # Madre, Padre, Tutor, Tío/a, etc.
    telefono = db.Column(db.String(30), nullable=True)
    whatsapp = db.Column(db.String(30), nullable=True)
    correo = db.Column(db.String(100), nullable=True)
    direccion = db.Column(db.String(200), nullable=True)
    es_contacto_principal = db.Column(db.Boolean, default=True)
    es_contacto_emergencia = db.Column(db.Boolean, default=True)
    observaciones_salud = db.Column(db.String(255), nullable=True) # Alergias, medicamentos, etc.
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Familiar {self.nombres} ({self.parentesco}) - Estudiante ID: {self.estudiante_id}>'


# Aliases para compatibilidad con código existente
Section = Aula
Student = Estudiante

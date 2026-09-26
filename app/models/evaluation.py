from datetime import datetime, date
from app import db

class Asignatura(db.Model):
    """
    Modelo para Asignaturas del Plan de Estudio del Nivel Secundario (MINERD).
    Ejemplos: Lengua Española, Matemática, Ciencias Sociales, Ciencias de la Naturaleza, etc.
    """
    __tablename__ = 'asignaturas'

    id = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(20), unique=True, nullable=False) # 'ESP', 'MAT', 'SOC', 'NAT', 'ING', etc.
    nombre = db.Column(db.String(100), nullable=False)            # Nombre oficial de la materia
    area = db.Column(db.String(80), nullable=False)               # Área académica curricular
    ciclo = db.Column(db.String(50), default='Ambos')             # 'Primer Ciclo', 'Segundo Ciclo', 'Ambos'
    grado = db.Column(db.String(50), default='Todos')             # Grado específico o 'Todos'
    horas_semanales = db.Column(db.Integer, default=4)
    es_optativa = db.Column(db.Boolean, default=False)            # Salida optativa de 4.º a 6.º
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relaciones
    competencias_especificas = db.relationship('CompetenciaEspecifica', backref='asignatura', lazy=True, cascade='all, delete-orphan')
    contenidos_curriculares = db.relationship('ContenidoCurricular', backref='asignatura', lazy=True, cascade='all, delete-orphan')
    evaluaciones = db.relationship('Evaluacion', backref='asignatura', lazy=True, cascade='all, delete-orphan')
    asistencias = db.relationship('Asistencia', backref='asignatura', lazy=True)

    def __repr__(self):
        return f'<Asignatura {self.codigo} - {self.nombre}>'


class CompetenciaFundamental(db.Model):
    """
    Modelo para las 7 Competencias Fundamentales del Currículo Dominicano:
    1. Comunicativa
    2. Pensamiento Lógico, Creativo y Crítico
    3. Resolución de Problemas
    4. Científica y Tecnológica
    5. Ambiental y de la Salud
    6. Desarrollo Personal y Espiritual
    7. Ética y Ciudadana
    """
    __tablename__ = 'competencias_fundamentales'

    id = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(20), unique=True, nullable=False) # 'CF-COM', 'CF-PLC', etc.
    nombre = db.Column(db.String(120), unique=True, nullable=False)
    descripcion = db.Column(db.Text, nullable=True)

    # Relación con Competencias Específicas
    competencias_especificas = db.relationship('CompetenciaEspecifica', backref='competencia_fundamental', lazy=True)

    def __repr__(self):
        return f'<CompetenciaFundamental {self.codigo}: {self.nombre}>'


class CompetenciaEspecifica(db.Model):
    """
    Modelo para Competencias Específicas de cada Asignatura.
    Tributan directamente a una o más Competencias Fundamentales.
    """
    __tablename__ = 'competencias_especificas'

    id = db.Column(db.Integer, primary_key=True)
    asignatura_id = db.Column(db.Integer, db.ForeignKey('asignaturas.id'), nullable=True)
    competencia_fundamental_id = db.Column(db.Integer, db.ForeignKey('competencias_fundamentales.id'), nullable=True)
    grade_id = db.Column(db.Integer, db.ForeignKey('grade_levels.id'), nullable=True)
    
    codigo = db.Column(db.String(30), nullable=True, default='CE-01') # Ej: "CE-LE1", "CE-MAT1"
    name = db.Column(db.String(255), nullable=False)              # Nombre / Enunciado
    type = db.Column(db.String(50), default='Específica')         # 'Específica' / 'Fundamental'
    descripcion = db.Column(db.Text, nullable=True)
    ciclo = db.Column(db.String(50), nullable=True)
    grado = db.Column(db.String(50), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relaciones
    indicadores = db.relationship('IndicadorLogro', backref='competencia_especifica', lazy=True, cascade='all, delete-orphan')
    contenidos = db.relationship('ContenidoCurricular', backref='competencia_especifica', lazy=True)

    # Propiedades de compatibilidad con modelo anterior Competency
    @property
    def indicators(self):
        return self.indicadores

    @property
    def nombre(self):
        return self.name

    def __repr__(self):
        return f'<CompetenciaEspecifica {self.codigo} - {self.name}>'


class IndicadorLogro(db.Model):
    """
    Modelo para Indicadores de Logro (IL).
    Criterios de evaluación formativa y sumativa por competencia y período (P1 a P4).
    """
    __tablename__ = 'indicadores_logro'

    id = db.Column(db.Integer, primary_key=True)
    competency_id = db.Column(db.Integer, db.ForeignKey('competencias_especificas.id'), nullable=False)
    code = db.Column(db.String(30), nullable=False)               # Ej: "IL-1.1", "IL-2.1"
    description = db.Column(db.Text, nullable=False)              # Desempeño observable
    period = db.Column(db.String(10), default='Todos')            # 'P1', 'P2', 'P3', 'P4' o 'Todos'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relaciones
    evaluaciones = db.relationship('Evaluacion', backref='indicador_logro', lazy=True, cascade='all, delete-orphan')

    # Propiedades de compatibilidad
    @property
    def competency(self):
        return self.competencia_especifica

    @property
    def grades(self):
        return self.evaluaciones

    @property
    def codigo(self):
        return self.code

    @property
    def descripcion(self):
        return self.description

    def __repr__(self):
        return f'<IndicadorLogro {self.code}>'


class ContenidoCurricular(db.Model):
    """
    Modelo para Contenidos Curriculares por Período y Asignatura.
    Clasificados en Conceptuales, Procedimentales y Actitudinales.
    """
    __tablename__ = 'contenidos_curriculares'

    id = db.Column(db.Integer, primary_key=True)
    asignatura_id = db.Column(db.Integer, db.ForeignKey('asignaturas.id'), nullable=False)
    competencia_especifica_id = db.Column(db.Integer, db.ForeignKey('competencias_especificas.id'), nullable=True)
    periodo = db.Column(db.String(10), nullable=False)            # 'P1', 'P2', 'P3', 'P4'
    tema = db.Column(db.String(255), nullable=False)              # Tema o contenido clave
    tipo = db.Column(db.String(50), default='Conceptual')         # 'Conceptual', 'Procedimental', 'Actitudinal'
    descripcion = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<ContenidoCurricular {self.periodo} - {self.tema} ({self.tipo})>'


class Evaluacion(db.Model):
    """
    Modelo para Calificaciones y Evaluaciones de los Aprendizajes.
    Soporta los 4 períodos (P1, P2, P3, P4), Recuperación Pedagógica (RP),
    Completiva y Extraordinaria en escala 0-100 con mínimo aprobatorio de 70.
    """
    __tablename__ = 'evaluaciones'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('estudiantes.id'), nullable=False)
    asignatura_id = db.Column(db.Integer, db.ForeignKey('asignaturas.id'), nullable=False)
    indicator_id = db.Column(db.Integer, db.ForeignKey('indicadores_logro.id'), nullable=True)
    
    period = db.Column(db.String(10), nullable=False)             # 'P1', 'P2', 'P3', 'P4', 'C.F.'
    score = db.Column(db.Float, nullable=False, default=0.0)      # Calificación ordinaria (0 a 100)
    calificacion_recuperacion = db.Column(db.Float, nullable=True)# RP1, RP2, RP3, RP4
    calificacion_final_periodo = db.Column(db.Float, nullable=True) # Mayor entre score y RP
    tipo = db.Column(db.String(30), default='Ordinaria')          # 'Ordinaria', 'Recuperacion', 'Completiva', 'Extraordinaria'
    aprobado = db.Column(db.Boolean, default=True)
    observaciones = db.Column(db.String(255), nullable=True)
    # 4 Calificaciones Ordinarias por Competencia del Período (0-100)
    c1_score = db.Column(db.Float, nullable=True, default=0.0)
    c2_score = db.Column(db.Float, nullable=True, default=0.0)
    c3_score = db.Column(db.Float, nullable=True, default=0.0)
    c4_score = db.Column(db.Float, nullable=True, default=0.0)

    # 4 Calificaciones de Recuperación Pedagógica (RP) correspondientes a cada competencia
    c1_rp = db.Column(db.Float, nullable=True)
    c2_rp = db.Column(db.Float, nullable=True)
    c3_rp = db.Column(db.Float, nullable=True)
    c4_rp = db.Column(db.Float, nullable=True)

    @property
    def c1_final(self):
        if self.c1_rp is not None:
            return max(self.c1_score or 0.0, self.c1_rp)
        return self.c1_score or 0.0

    @property
    def c2_final(self):
        if self.c2_rp is not None:
            return max(self.c2_score or 0.0, self.c2_rp)
        return self.c2_score or 0.0

    @property
    def c3_final(self):
        if self.c3_rp is not None:
            return max(self.c3_score or 0.0, self.c3_rp)
        return self.c3_score or 0.0

    @property
    def c4_final(self):
        if self.c4_rp is not None:
            return max(self.c4_score or 0.0, self.c4_rp)
        return self.c4_score or 0.0

    @property
    def has_rp_needed(self):
        scores = [self.c1_score or 0.0, self.c2_score or 0.0, self.c3_score or 0.0, self.c4_score or 0.0]
        return any(s < 70 for s in scores)

    # Propiedades de compatibilidad
    @property
    def estudiante_id(self):
        return self.student_id

    @property
    def periodo(self):
        return self.period

    @property
    def calificacion(self):
        return self.score

    @property
    def student(self):
        return self.estudiante

    @property
    def indicator(self):
        return self.indicador_logro

    def __repr__(self):
        return f'<Evaluacion Estudiante:{self.student_id} Asignatura:{self.asignatura_id} {self.period}: {self.score}>'


class Seguimiento(db.Model):
    """
    Modelo para Seguimiento Pedagógico, Ausentismo y Orientación Psicológica.
    Registra alertas tempranas (Regla de 3 Ausencias), citaciones a tutores y compromisos.
    """
    __tablename__ = 'seguimientos'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('estudiantes.id'), nullable=False)
    aula_id = db.Column(db.Integer, db.ForeignKey('aulas.id'), nullable=True)
    fecha = db.Column(db.Date, default=date.today, nullable=False)
    
    tipo = db.Column(db.String(60), nullable=False)               # 'Alerta 3 Ausencias', 'Bajo Rendimiento', 'Citación a Padres', 'Intervención de Orientación'
    motivo = db.Column(db.String(255), nullable=False)
    descripcion = db.Column(db.Text, nullable=True)
    acciones_acordadas = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(30), default='Abierto')          # 'Abierto', 'En Proceso', 'Resuelto', 'Cerrado'
    responsable = db.Column(db.String(120), default='Departamento de Orientación y Psicología')
    fecha_resolucion = db.Column(db.Date, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Propiedades de compatibilidad con modelo anterior PedagogicalRecovery
    @property
    def estudiante_id(self):
        return self.student_id

    @property
    def estado(self):
        return self.status

    @property
    def student(self):
        return self.estudiante

    @property
    def notes(self):
        return self.descripcion

    def __repr__(self):
        return f'<Seguimiento Estudiante:{self.student_id} Tipo:{self.tipo} Estado:{self.status}>'


class Reporte(db.Model):
    """
    Modelo para Registro y Auditoría de Reportes Oficiales Generados.
    Almacena metadatos de fichas de seguimiento, boletines de notas y sábanas impresas.
    """
    __tablename__ = 'reportes'

    id = db.Column(db.Integer, primary_key=True)
    tipo_reporte = db.Column(db.String(80), nullable=False)       # 'Ficha de Seguimiento de Asistencia', 'Boletín de Calificaciones', 'Sábana Oficial', 'Acta Final'
    estudiante_id = db.Column(db.Integer, db.ForeignKey('estudiantes.id'), nullable=True)
    aula_id = db.Column(db.Integer, db.ForeignKey('aulas.id'), nullable=True)
    periodo = db.Column(db.String(20), nullable=True)             # 'P1', 'P2', 'P3', 'P4', 'Final'
    titulo = db.Column(db.String(150), nullable=False)
    archivo_generado = db.Column(db.String(255), nullable=True)   # Ruta al PDF/HTML generado
    generado_por = db.Column(db.String(100), default='Sistema EduReport')
    datos_json = db.Column(db.Text, nullable=True)                # Snapshot de datos del reporte
    fecha_generacion = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Reporte ID:{self.id} Tipo:{self.tipo_reporte} Titulo:{self.titulo}>'


# Aliases de compatibilidad con código existente
Competency = CompetenciaEspecifica
Indicator = IndicadorLogro
Grade = Evaluacion
PedagogicalRecovery = Seguimiento

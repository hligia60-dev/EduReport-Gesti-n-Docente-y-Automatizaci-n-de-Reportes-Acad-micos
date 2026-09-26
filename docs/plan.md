# Plan Integral del Proyecto: EduReport
**Sistema de Gestión Docente y Generación Automática de Reportes Académicos**

---

## 1. Problema
En las instituciones de Educación Secundaria, la gestión académica tradicional (mediante registros físicos en papel, cuadernos de notas o archivos dispersos de hojas de cálculo) presenta serias dificultades que impactan la labor pedagógica:
- **Carga administrativa excesiva:** Los docentes dedican una cantidad desproporcionada de tiempo al cálculo manual de promedios, porcentajes de asistencia y ponderaciones de competencias.
- **Detección tardía del ausentismo escolar:** Al no contar con un sistema automatizado de alertas tempranas, las inasistencias reiteradas suelen detectarse cuando el estudiante ya está en riesgo inminente de reprobación o deserción escolar.
- **Complejidad del diseño curricular por competencias:** La división curricular en **Primer Ciclo (1.º, 2.º y 3.º de Secundaria)** y **Segundo Ciclo (4.º, 5.º y 6.º de Secundaria)** requiere un seguimiento minucioso de competencias fundamentales, específicas e indicadores de logro a lo largo de cuatro períodos de evaluación (**P1, P2, P3, P4**), sumado a los procesos de **recuperación pedagógica**.
- **Generación lenta e inconsistente de reportes:** La elaboración manual de boletines de calificaciones, sábanas de notas e informes de citación a tutores propicia errores humanos y carece de estandarización visual.

---

## 2. Usuarios
El sistema define roles claros adaptados a la dinámica de los centros educativos:
1. **Docente de Aula / Asignatura (Usuario Principal):**
   - Administra sus secciones asignadas en Primer y Segundo Ciclo.
   - Realiza el pase de lista diario y registra observaciones.
   - Evalúa los indicadores de logro por período.
   - Aplica y registra calificaciones de recuperación pedagógica.
   - Emite boletines y fichas de seguimiento.
2. **Coordinador Pedagógico / Departamento de Orientación y Psicología:**
   - Supervisa el rendimiento global de los ciclos y grados.
   - Recibe alertas automáticas cuando un estudiante acumula **3 ausencias** para iniciar el protocolo de intervención y citación familiar.
3. **Equipo Directivo y Secretaría Docente:**
   - Consulta sábanas consolidadas de calificaciones para fines de archivo y validación oficial.
   - Analiza estadísticas de retención escolar y promoción de grado.

---

## 3. Objetivo
Desarrollar una aplicación web educativa con **Python y Flask**, diseñada bajo principios de arquitectura limpia, modular y pedagógica, que centralice la gestión docente en el Nivel Secundario (1.º a 6.º grado), automatice la evaluación formativa y sumativa por competencias en cuatro períodos, active alertas tempranas ante **3 ausencias acumuladas** y genere reportes académicos formales listos para impresión y exportación digital.

---

## 4. Solución
**EduReport** es una solución web integral, moderna y ligera que ofrece:
- **Landing Page Institucional:** Página de presentación con identidad visual profesional que expone las bondades del sistema y facilita el acceso.
- **Panel de Control (Dashboard Docente):** Centro de mando con métricas en tiempo real: total de estudiantes, secciones activas, alertas críticas de asistencia y estado de avance de calificaciones.
- **Módulo de Asistencia Inteligente:** Registro ágil diario con un detector automático que activa una alerta preventiva y habilita la emisión instantánea del *Informe de Seguimiento de Asistencia* cuando un alumno alcanza 3 faltas.
- **Gestor Curricular de Calificaciones:** Planilla electrónica adaptada a la normativa educativa con soporte de competencias, períodos (P1 a P4) y recuperación pedagógica integrada.
- **Generador de Reportes Formales:** Documentos oficiales con diseño institucional y reglas de estilo para impresión directa (`@media print` / PDF).

---

## 5. Funcionalidades del Sistema

### A. Módulo Institucional y Acceso
- **Landing Page atractiva:** Presentación pública del sistema, misión institucional, características y acceso al portal.
- **Autenticación Docente:** Sistema seguro de inicio y cierre de sesión con almacenamiento seguro de credenciales mediante hash criptográfico (`werkzeug.security`).

### B. Estructura Académica (Nivel Secundario)
- **Gestión por Ciclos y Grados:**
  - **Primer Ciclo:** 1.º, 2.º y 3.º de Secundaria.
  - **Segundo Ciclo:** 4.º, 5.º y 6.º de Secundaria (soporte para modalidades general y técnica).
- **Gestión de Secciones y Estudiantes:**
  - Creación de secciones (A, B, C, etc.) por año escolar.
  - Registro de alumnos: matrícula escolar, nombres, apellidos, datos de contacto del tutor legal y estado de escolaridad.

### C. Control de Asistencia y Alerta Temprana (Regla Específica)
- Registro diario de asistencia con estados: *Presente*, *Ausente*, *Tardanza*, *Excusa justificada*.
- **Regla Específica de Negocio:**
  - Al acumular **3 ausencias**, el sistema activa una alerta visual destacada (indicador/badge de atención inmediata en el panel y en la lista de alumnos).
  - Permite generar directamente el **Informe de Seguimiento de Asistencia**, un documento formal con el desglose de fechas, motivos y casillas para las firmas del Docente, Orientación y el Tutor.

### D. Evaluación por Competencias, Períodos y Recuperación
- Registro ordenado de calificaciones en los cuatro períodos lectivos (**P1, P2, P3, P4**).
- Evaluación desglosada por **Competencias Fundamentales y Específicas** con sus respectivos **Indicadores de Logro**.
- **Módulo de Recuperación Pedagógica:**
  - Identificación automática de estudiantes que no alcancen la puntuación mínima de aprobación (70 puntos).
  - Registro de evaluación de recuperación pedagógica, cálculo del promedio final ajustado y trazabilidad de la nota original vs. nota recuperada.

### E. Módulo de Reportes e Impresión
- **Boletín de Calificaciones Individual:** Informe detallado por estudiante con el progreso en cada período, competencias y resultado final.
- **Informe de Alerta y Seguimiento de Asistencia:** Ficha emitida ante 3 faltas acumuladas para intervención con el hogar.
- **Sábana General de Calificaciones:** Matriz consolidada del curso para secretaría y dirección.
- **Resumen Estadístico:** Indicadores visuales de tasa de aprobación, reprobación y porcentaje de asistencia.

---

## 6. Tecnologías

| Componente | Tecnología | Justificación y Rol |
| :--- | :--- | :--- |
| **Lenguaje** | **Python 3.10+** | Lenguaje obligatorio, potente, limpio y didáctico para enseñar buenas prácticas de backend. |
| **Entorno Virtual** | **`.venv`** | Aislamiento completo de paquetes y dependencias del proyecto. |
| **Framework Web** | **Flask** | Framework ligero, explícito y modular que permite comprender el flujo HTTP y el patrón MVC sin abstracciones complejas innecesarias. |
| **Base de Datos y ORM** | **SQLite + Flask-SQLAlchemy** | Almacenamiento relacional sin necesidad de instalar servidores de bases de datos externos; portabilidad absoluta en archivo local `.db`. |
| **Motor de Vistas** | **Jinja2** | Renderizado del lado del servidor de plantillas HTML reutilizables mediante herencia de layouts (`{% extends %}`). |
| **Frontend / Diseño** | **HTML5 + CSS3 + Bootstrap 5.3** | Maquetación responsiva, moderna y accesible combinada con estilos CSS propios para una identidad visual premium. |
| **Iconografía** | **Bootstrap Icons** | Conjunto completo de iconos vectoriales para acciones, estados y alertas. |
| **Control de Versiones** | **Git & GitHub** | Gestión del historial de desarrollo, ramas de trabajo y publicación en repositorio remoto. |

---

## 7. Arquitectura Propuesta

Se implementará el **Patrón de Fábrica de Aplicaciones (Application Factory Pattern)** junto con **Blueprints** de Flask para garantizar modularidad, bajo acoplamiento y facilidad de comprensión:

```
                      [ Cliente Web / Navegador ]
                                  │  ▲
                     Petición HTTP│  │Respuesta HTML / CSS
                                  ▼  │
                     ┌─────────────────────────────┐
                     │   Flask App Core (run.py)   │
                     │         create_app()        │
                     └──────────────┬──────────────┘
                                    │ Registra Blueprints
      ┌──────────────┬──────────────┼──────────────┬──────────────┐
      ▼              ▼              ▼              ▼              ▼
 [bp: main]     [bp: auth]    [bp: students]  [bp: attend]   [bp: grades]
Landing Page      Login         Gestión de     Pase de lista   Notas P1-P4
 Dashboard       Logout         1.º a 6.º      Regla 3 Faltas Recuperación
      │              │              │              │              │
      └──────────────┴──────────────┼──────────────┴──────────────┘
                                    ▼
                      [ Capa de Servicios / Lógica ]
                       - attendance_service.py (Verificador de 3 faltas)
                       - grade_service.py (Cálculo de notas y recuperación)
                       - report_service.py (Preparación de datos imprimibles)
                                    │
                                    ▼
                      [ Modelos de Datos (ORM) ]
                       Flask-SQLAlchemy (Entities)
                                    │
                                    ▼
                      [ Base de Datos: SQLite ]
```

---

## 8. Estructura de Carpetas

```text
EduReport/
│
├── .venv/                         # Entorno virtual de Python (ignorado en Git)
├── .gitignore                     # Reglas de exclusión para Git
├── requirements.txt               # Dependencias del proyecto (Flask, SQLAlchemy, etc.)
├── run.py                         # Punto de entrada para ejecutar el servidor
├── config.py                      # Clases de configuración (Development, Testing, Production)
├── README.md                      # Presentación formal y guía de instalación rápida
│
├── docs/                          # Documentación del proyecto
│   ├── plan.md                    # Plan integral aprobado del proyecto
│   ├── tutorial.md                # Guía didáctica paso a paso para principiantes
│   ├── arquitectura.md            # Documento técnico detallado de la arquitectura
│   └── images/
│       └── arquitectura.png       # Diagrama visual de la arquitectura
│
└── app/                           # Paquete principal de la aplicación Flask
    ├── __init__.py                # Fábrica de la app (create_app), extensiones y Blueprints
    │
    ├── models/                    # Modelos de datos (Capa de datos)
    │   ├── __init__.py
    │   ├── user.py                # Modelo de Docente/Usuario
    │   ├── academic.py            # Ciclo, Grado (1.º a 6.º), Sección y Estudiante
    │   ├── attendance.py          # Registro diario de Asistencia
    │   └── evaluation.py          # Competencias, Indicadores, Calificaciones y Recuperación
    │
    ├── routes/                    # Controladores (Rutas por Blueprints)
    │   ├── __init__.py
    │   ├── main_routes.py         # Landing Page y Dashboard principal
    │   ├── auth_routes.py         # Autenticación (Login, Logout)
    │   ├── student_routes.py      # Directorio de estudiantes y secciones
    │   ├── attendance_routes.py   # Pase de lista y panel de alertas de inasistencias
    │   ├── grade_routes.py        # Registro de calificaciones y recuperación pedagógica
    │   └── report_routes.py       # Vistas de impresión y exportación de reportes
    │
    ├── services/                  # Lógica de negocio independiente de las rutas
    │   ├── __init__.py
    │   ├── attendance_service.py  # Detección de ausencias acumuladas y activación de alertas
    │   ├── grade_service.py       # Ponderaciones de períodos y reglas de recuperación
    │   └── report_service.py      # Estructuración de datos para reportes y boletines
    │
    ├── static/                    # Archivos estáticos
    │   ├── css/
    │   │   ├── style.css          # Estilos visuales del sistema (paleta moderna, tipografía)
    │   │   └── print.css          # Reglas de impresión para reportes limpios (oculta navbars/botones)
    │   ├── js/
    │   │   └── main.js            # Interacciones dinámicas en el cliente (validaciones, alertas)
    │   └── img/
    │       └── logo.svg           # Identidad gráfica institucional
    │
    └── templates/                 # Plantillas HTML con motor Jinja2
        ├── base.html              # Plantilla maestra (Navbar, Sidebar, mensajes flash y scripts)
        ├── landing.html           # Landing page pública institucional
        ├── auth/
        │   └── login.html         # Formulario de inicio de sesión docente
        ├── dashboard/
        │   └── index.html         # Tablero principal con estadísticas y alertas críticas
        ├── students/
        │   ├── list.html          # Listado por grado/sección con filtros
        │   └── form.html          # Formulario de creación/edición de estudiante
        ├── attendance/
        │   ├── register.html      # Planilla de pase de lista diario
        │   └── alert_list.html    # Bandeja de seguimiento a estudiantes con 3 o más ausencias
        ├── grades/
        │   ├── register.html      # Registro de calificaciones por indicadores y períodos (P1-P4)
        │   └── recovery.html      # Registro y control de recuperación pedagógica
        └── reports/
            ├── student_card.html  # Boletín oficial de calificaciones por estudiante
            ├── attendance_report.html # Informe de seguimiento y citación por 3 ausencias
            └── section_sheet.html # Sábana consolidada de calificaciones del curso
```

---

## 9. Modelo de Base de Datos Relacional

La base de datos se estructura bajo el principio de normalización relacional:

1. **`User` (Usuario/Docente):**
   - Atributos: `id`, `name`, `email`, `password_hash`, `role`, `created_at`.
2. **`Cycle` (Ciclo del Nivel Secundario):**
   - Atributos: `id`, `name` (*Primer Ciclo*, *Segundo Ciclo*).
3. **`GradeLevel` (Grado Académico):**
   - Atributos: `id`, `cycle_id` (FK), `name` (*1.º, 2.º, 3.º, 4.º, 5.º, 6.º*).
4. **`Section` (Sección):**
   - Atributos: `id`, `grade_id` (FK), `name` (*A, B, C...*), `school_year`.
5. **`Student` (Estudiante):**
   - Atributos: `id`, `section_id` (FK), `registration_number` (Matrícula única), `first_name`, `last_name`, `tutor_name`, `tutor_phone`, `is_active`.
6. **`Attendance` (Asistencia):**
   - Atributos: `id`, `student_id` (FK), `date`, `status` (*Presente, Ausente, Tardanza, Excusa*), `notes`.
7. **`Competency` (Competencia Curricular):**
   - Atributos: `id`, `grade_id` (FK), `name`, `type` (*Fundamental, Específica*).
8. **`Indicator` (Indicador de Logro):**
   - Atributos: `id`, `competency_id` (FK), `code`, `description`.
9. **`Grade` (Calificación):**
   - Atributos: `id`, `student_id` (FK), `indicator_id` (FK), `period` (*P1, P2, P3, P4*), `score`.
10. **`PedagogicalRecovery` (Recuperación Pedagógica):**
    - Atributos: `id`, `student_id` (FK), `period_or_final`, `original_score`, `recovery_score`, `status` (*Aprobado, Reprobado*), `recovery_date`.

---

## 10. Estrategia de Reportes
Los reportes se elaborarán con maquetación web de alta fidelidad y hojas de estilo optimizadas para impresión (`@media print`):
1. **Informe de Seguimiento de Asistencia (Regla de 3 Ausencias):**
   - Encabezado con datos del centro educativo y del estudiante.
   - Historial detallado de las fechas exactas de inasistencia y notas registradas.
   - Espacios formales para compromisos y firmas del Docente, Orientador y Tutor legal.
2. **Boletín Individual de Calificaciones:**
   - Tabla comprensiva de calificaciones por competencias en los períodos P1, P2, P3 y P4.
   - Sección explícita de resultados de Recuperación Pedagógica en caso de aplicar.
   - Promedio final y estado de aprobación.
3. **Sábana de Calificaciones del Curso:**
   - Vista en cuadrícula con el resumen de todos los estudiantes de la sección para el archivo docente y secretaría.

---

## 11. Estrategia de Pruebas (Testing)
Para garantizar la calidad académica del software:
- **Pruebas Unitarias (`unittest` / `pytest`):**
  - Validación de la lógica de alerta al acumular 3 ausencias en `attendance_service.py`.
  - Verificación del cálculo de promedios de períodos y determinación del umbral de recuperación (< 70 puntos).
  - Comprobación de modelos ORM y relaciones entre grados, secciones y alumnos.
- **Pruebas de Integración:**
  - Comprobación de respuestas HTTP de rutas públicas y autenticadas.
- **Pruebas de Usabilidad e Interfaz:**
  - Verificación visual del comportamiento responsivo y de la visualización previa de impresión en navegadores.

---

## 12. Plan de Documentación Académica
El repositorio contará con documentación integral orientada a principiantes:
- **`README.md`:** Portada del proyecto, descripción, captura de pantalla, requisitos previos, instrucciones de instalación paso a paso e inicio del servidor.
- **`docs/tutorial.md`:** Manual paso a paso para estudiantes y docentes principiantes (creación y activación del `.venv`, instalación de librerías con `pip`, comandos de inicialización y flujo completo de uso).
- **`docs/arquitectura.md`:** Justificación del patrón de diseño Application Factory, flujo de peticiones, diseño del modelo relacional y explicaciones técnicas de cada módulo.
- **`docs/images/arquitectura.png`:** Representación gráfica diagramada de la arquitectura de la aplicación.

---

## 13. Estrategia con Git y GitHub
- **Inicialización de repositorio Git:** Con rama principal `main`.
- **Archivo `.gitignore` configurado estrictamente para Python:**
  - Exclusión del entorno virtual (`.venv/`).
  - Exclusión de archivos binarios y temporales (`__pycache__/`, `*.pyc`).
  - Exclusión de base de datos local SQLite (`*.db`).
  - Exclusión de variables de entorno (`.env`).
- **Convención de Commits Semánticos:**
  - `feat:` Nuevas funcionalidades o módulos.
  - `fix:` Correcciones de errores o ajustes lógicos.
  - `docs:` Documentación, manuales y diagramas.
  - `style:` Mejoras estéticas de CSS o plantillas Bootstrap.

---

## 14. Etapas de Desarrollo

| Etapa | Nombre | Entregables Principales |
| :---: | :--- | :--- |
| **Fase 1** | **Estructura Base y Entorno** | Creación del `.venv`, `requirements.txt`, `.gitignore`, estructura de carpetas modular y configuración base de Flask (`run.py`, `config.py`, `app/__init__.py`). |
| **Fase 2** | **Base de Datos y Modelos** | Definición de modelos SQLAlchemy (Usuarios, Grados 1.º a 6.º, Secciones, Estudiantes, Asistencia, Calificaciones, Recuperación) y script de seed con datos iniciales. |
| **Fase 3** | **Landing Page y Autenticación** | Diseño visual de la Landing Page institucional, sistema de login docente y panel principal (Dashboard). |
| **Fase 4** | **Módulo de Estudiantes y Secciones** | Visualización de Primer Ciclo (1.º, 2.º, 3.º) y Segundo Ciclo (4.º, 5.º, 6.º), listados y registro de alumnos. |
| **Fase 5** | **Módulo de Asistencia y Alerta de 3 Faltas** | Formulario diario de pase de lista, contador automático de ausencias acumuladas, badges de alerta y botón de informe de seguimiento. |
| **Fase 6** | **Módulo de Calificaciones y Recuperación** | Registro de calificaciones por competencias en P1, P2, P3 y P4, detección de reprobados y registro de recuperación pedagógica. |
| **Fase 7** | **Módulo de Reportes Formatos Imprimibles** | Creación de plantillas optimizadas para impresión (Boletín individual, Informe de 3 ausencias, Sábana de curso). |
| **Fase 8** | **Documentación, Pruebas y Cierre** | Redacción de `README.md`, `docs/tutorial.md`, `docs/arquitectura.md`, generación del diagrama `docs/images/arquitectura.png` y pruebas unitarias. |

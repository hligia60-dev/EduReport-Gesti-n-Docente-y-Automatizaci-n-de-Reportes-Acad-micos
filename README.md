# 🎓 EduReport
**Sistema de Gestión Docente y Generación Automática de Reportes Académicos**

EduReport es una plataforma web académica desarrollada con **Python y Flask**, diseñada para simplificar la labor docente en el **Nivel Secundario (Primer Ciclo: 1.º, 2.º y 3.º; Segundo Ciclo: 4.º, 5.º y 6.º)**. Permite el control eficiente de asistencia con detección temprana de ausentismo, registro de evaluaciones por competencias y períodos (P1 a P4), control de recuperación pedagógica y emisión automática de reportes formales listos para imprimir o exportar a PDF.

---

## 🏛️ Diagrama de Arquitectura
El sistema está construido bajo el patrón modular **Application Factory** y **Blueprints** en Flask:

![Arquitectura de EduReport](docs/images/arquitectura.png)

Para una explicación didáctica completa para principiantes, consulta [docs/arquitectura.md](docs/arquitectura.md).

---

## 📁 Estructura del Proyecto

```text
EduReport/
│
├── app/                           # Paquete principal de la aplicación Flask
│   ├── __init__.py                # Fábrica de aplicaciones (create_app)
│   ├── routes/                    # Controladores y rutas (Blueprints)
│   ├── templates/                 # Plantillas HTML con motor Jinja2
│   ├── static/                    # Archivos estáticos
│   │   ├── css/                   # Estilos personalizados y de impresión
│   │   ├── js/                    # Scripts de interactividad en el cliente
│   │   └── img/                   # Logotipos e iconos
│   ├── models/                    # Modelos de base de datos (SQLAlchemy ORM)
│   ├── services/                  # Lógica de negocio (alertas, promedios, reportes)
│   └── utils/                     # Funciones y utilidades auxiliares
│
├── database/                      # Almacenamiento local de base de datos SQLite
├── reports/                       # Módulo de reportes
│   └── generated/                 # Informes y documentos generados
├── imports/                       # Archivos de carga masiva / plantillas
├── tests/                         # Pruebas unitarias y de integración
├── docs/                          # Documentación del proyecto
│   ├── plan.md                    # Plan integral del proyecto (14 puntos)
│   ├── arquitectura.md            # Explicación técnica de la arquitectura
│   └── images/
│       └── arquitectura.png       # Diagrama visual de la arquitectura
│
├── .gitignore                     # Archivos y carpetas excluidas de Git
├── requirements.txt               # Dependencias de Python del proyecto
├── README.md                      # Presentación formal del repositorio
├── config.py                      # Configuraciones de desarrollo, pruebas y producción
└── run.py                         # Punto de entrada para iniciar la aplicación
```

---

## 🛠️ Tecnologías Utilizadas

- **Backend:** Python 3.10+, Flask 3.x, Flask-SQLAlchemy, Werkzeug.
- **Frontend:** HTML5 semántico, CSS3, Bootstrap 5.3, Bootstrap Icons, Jinja2.
- **Base de Datos:** SQLite (archivo local relacional sin dependencias de servidor).
- **Control de Versiones:** Git y GitHub.

---

## ⚡ Regla Específica de Negocio: Alerta de Asistencia

> **Regla de 3 Ausencias:**
> Cuando un estudiante acumula **3 ausencias**, el sistema activa automáticamente un badge de alerta visible y habilita la generación instantánea del **Informe de Seguimiento de Asistencia** formal, con espacios para las firmas del Docente, Orientación y el Tutor.

---

## 🚀 Instalación y Puesta en Marcha

### 1. Clonar el repositorio
```bash
git clone https://github.com/usuario/EduReport.git
cd EduReport
```

### 2. Crear y activar el entorno virtual
En Windows:
```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
```

En Linux / macOS:
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 4. Iniciar el servidor de desarrollo
```bash
python run.py
```
Accede en tu navegador a: `http://127.0.0.1:5000`

---

## 📚 Documentación Adicional
- 📋 [Plan del Proyecto (14 puntos)](docs/plan.md)
- 🏛️ [Arquitectura de Software Detallada](docs/arquitectura.md)
- 🖼️ [Diagrama Visual de Arquitectura](docs/images/arquitectura.png)

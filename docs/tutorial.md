# 📘 Tutorial de Inicio Rápido: EduReport

¡Te damos la bienvenida a **EduReport**! 

Si estás dando tus primeros pasos en el mundo de la programación y el desarrollo web con Python, esta guía fue escrita especialmente para ti. Aquí aprenderás, paso a paso y con explicaciones sencillas, cómo poner a funcionar este sistema en tu computadora desde cero.

---

## Índice del Tutorial

1. [Obtener o clonar el proyecto](#paso-1-obtener-o-clonar-el-proyecto)
2. [Entrar a la carpeta del proyecto](#paso-2-entrar-a-la-carpeta-del-proyecto)
3. [Crear el entorno virtual (.venv)](#paso-3-crear-el-entorno-virtual-venv)
4. [Activar el entorno virtual](#paso-4-activar-el-entorno-virtual)
5. [Instalar las dependencias (requirements.txt)](#paso-5-instalar-las-dependencias-requirementstxt)
6. [Ejecutar la aplicación con Flask](#paso-6-ejecutar-la-aplicación-con-flask)
7. [Abrir el navegador web](#paso-7-abrir-el-navegador-web)
8. [Aprender a utilizar EduReport](#paso-8-aprender-a-utilizar-edureport)
9. [Detener la aplicación](#paso-9-detener-la-aplicación)
10. [Desactivar el entorno virtual](#paso-10-desactivar-el-entorno-virtual)

---

### Paso 1: Obtener o clonar el proyecto

Para traer una copia del código a tu computadora, abrimos una ventana de terminal (**PowerShell** o **Símbolo del sistema (CMD)** en Windows, o la **Terminal** en Mac o Linux).

Escribe el siguiente comando y presiona la tecla **Enter**:

```bash
git clone https://github.com/usuario/EduReport.git
```

> **¿Qué hace este comando?**
> `git clone` descarga todos los archivos, carpetas e imágenes del proyecto desde internet y los guarda en tu máquina.

---

### Paso 2: Entrar a la carpeta del proyecto

Una vez que termine la descarga, debes ingresar dentro de la carpeta que se acaba de crear:

```bash
cd EduReport
```

> **¿Qué significa `cd`?**
> Significa *Change Directory* (cambiar de carpeta). Ahora tu terminal se encuentra situada dentro del proyecto EduReport.

---

### Paso 3: Crear el entorno virtual (.venv)

Un **entorno virtual** es como una pequeña caja de herramientas aislada. Permite que instalemos los programas y librerías que necesita EduReport sin alterar ni ensuciar el resto de tu computadora.

Para crearlo, escribe:

#### En Windows:
```powershell
python -m venv .venv
```

#### En Mac o Linux:
```bash
python3 -m venv .venv
```

> **¿Qué ocurre tras bambalinas?**
> Python creará una carpetita llamada `.venv` que contiene una copia limpia y exclusiva de Python para este proyecto.

---

### Paso 4: Activar el entorno virtual

Ahora debemos decirle a la terminal que use la caja de herramientas que acabamos de crear.

#### En Windows (PowerShell):
```powershell
.\.venv\Scripts\Activate.ps1
```

*(Si usas la consola clásica de Windows **CMD**, escribe: `.venv\Scripts\activate.bat`)*

#### En Mac o Linux:
```bash
source .venv/bin/activate
```

> **¿Cómo sé que funcionó?**
> Sabrás que el entorno virtual está activo porque al principio de la línea de tu terminal aparecerá la palabra **`(.venv)`** entre paréntesis, así:
> `(.venv) C:\Users\TuNombre\EduReport>`

---

### Paso 5: Instalar las dependencias (requirements.txt)

El archivo `requirements.txt` es como la lista de compras del proyecto: enumera todas las librerías necesarias (como Flask, SQLAlchemy y ReportLab).

Para instalarlas todas de una sola vez, ejecuta:

```bash
pip install -r requirements.txt
```

> **¿Qué hace `pip`?**
> `pip` es el instalador de paquetes de Python. Leerá el archivo e instalará automáticamente:
> - **Flask:** El motor web.
> - **Flask-SQLAlchemy:** El conector para la base de datos de estudiantes y notas.
> - **ReportLab:** La herramienta que dibuja y genera los reportes en PDF.
> - **Pillow:** El procesador de imágenes para los escudos y logos.

---

### Paso 6: Ejecutar la aplicación con Flask

¡Ya tenemos todo listo para encender la aplicación! Escribe en tu terminal:

```bash
python run.py
```

En la pantalla verás un texto similar a este:

```text
 * Serving Flask app 'app'
 * Debug mode: on
 * Running on all addresses (0.0.0.0)
 * Running on http://127.0.0.1:5000
 * Debugger is active!
```

> **¡Felicidades!** Tu servidor web local ya está vivo y funcionando en tu propia computadora.

---

### Paso 7: Abrir el navegador web

Deja la terminal abierta (no la cierres, ya que es el motor que mantiene viva la aplicación).

Abre tu navegador de internet favorito (Google Chrome, Microsoft Edge, Firefox, Brave o Safari) y escribe en la barra de direcciones:

```text
http://127.0.0.1:5000
```
*(También puedes escribir `http://localhost:5000`)*.

Presiona **Enter** y verás la pantalla principal de **EduReport**.

---

### Paso 8: Aprender a utilizar EduReport

Exploremos las secciones principales que puedes usar:

1. **Dashboard (`/dashboard`):**
   - Aquí verás el resumen de estudiantes matriculados en 1.er Ciclo (1.º, 2.º y 3.º) y 2.do Ciclo (4.º, 5.º y 6.º).
   - Encontrarás gráficos interactivos de asistencia global y el indicador de alertas.

2. **Estudiantes (`/estudiantes`):**
   - Haz clic en **"+ Registrar Nuevo Estudiante"** para agregar un nuevo alumno con su nombre, RNE, grado, sección, condición y datos de su tutor.
   - Puedes buscar a cualquier estudiante por apellido o matrícula.
   - Al hacer clic en el nombre de un estudiante, verás su expediente individual.

3. **Asistencia y Pase de Lista (`/asistencia/diaria`):**
   - Selecciona el aula y la fecha.
   - Marca para cada estudiante su estado: **P** (Presente), **T** (Tardanza), **A** (Ausente) o **E** (Excusa).
   - Guarda los cambios.
   - **Regla de las 3 Ausencias:** Si un estudiante acumula 3 faltas, el sistema lo marcará en rojo con una alerta inmediata.

4. **Bandeja de Alertas (`/asistencia/alertas`):**
   - Muestra a todos los estudiantes que tienen 3 o más ausencias acumuladas.
   - Cada uno tiene un botón rojo para generar de inmediato su informe oficial.

5. **Evaluaciones Académicas (`/evaluaciones`):**
   - Registra calificaciones en escala de 0 a 100 para los períodos P1, P2, P3 y P4.
   - Si el estudiante obtuvo menos de 70 puntos, puedes registrar su nota de **Recuperación Pedagógica (RP)**.
   - Visualiza el gráfico de evolución de calificaciones entre períodos.

6. **Generador de Reportes y Descarga de PDF (`/reportes`):**
   - Elige el tipo de reporte: Asistencia, Avance Académico o Bajo Rendimiento.
   - Revisa la vista previa del borrador.
   - Presiona el botón rojo **"Descargar PDF Oficial"** para obtener en tu computadora el documento listo para imprimir con escudo, sellos y 4 espacios para firmas.

---

### Paso 9: Detener la aplicación

Cuando hayas terminado de usar o probar EduReport:

1. Regresa a la ventana de la terminal donde corre el programa.
2. Presiona en tu teclado la combinación de teclas:
   ```text
   Ctrl + C
   ```
3. El servidor se detendrá y volverás a tener disponible la línea de comandos normal.

---

### Paso 10: Desactivar el entorno virtual

Para salir del entorno virtual y volver al estado habitual de tu computadora, escribe:

```bash
deactivate
```

Notarás que la palabra `(.venv)` desaparecerá del inicio de tu terminal. ¡Eso es todo!

---

## 💡 Consejos para Principiantes

- **Para volver a abrir el proyecto otro día:** Solo necesitas hacer el **Paso 2** (`cd EduReport`), el **Paso 4** (activar `.venv`) y el **Paso 6** (`python run.py`). ¡No necesitas volver a instalar nada!
- **Para ejecutar las pruebas del sistema:** Activa tu entorno y corre `python -m unittest tests/test_edureport_core.py`. Verás cómo la computadora prueba automáticamente cada función en menos de 1 segundo.

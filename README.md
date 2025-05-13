# Proyecto Verificable - Kanvas

Este repositorio contiene **Kanvas**, una plataforma educativa desarrollada con **Flask**. A continuación, encontrarás una guía paso a paso para configurar el entorno, iniciar la aplicación y entender la estructura del proyecto.

---

## 🚀 Configuración del Proyecto

Sigue estos pasos para poner en marcha el proyecto:

### 1. Clona el repositorio

```bash
git clone https://github.com/AlbertoZuiga/verificable-grupo-8.git
cd verificable-grupo-8
```

### 2. **Crear un entorno virtual**:

- En Linux/macOS:
  ```bash
   python3 -m venv venv
   source venv/bin/activate
  ```
- En Windows (CMD o PowerShell):
  ```powershell
   python -m venv venv
   .\venv\Scripts\activate
  ```

### 3. **Instalar las dependencias**:

- En Linux/macOS:
  ```bash
   pip3 install -r requirements.txt
  ```
- En Windows (CMD o PowerShell):
  ```powershell
   pip install -r requirements.txt
  ```

### 4. **Configurar la base de datos**:

- Asegúrate de tener MySQL instalado y configurado en tu dispositivo.
- Crea un archivo `.env` en la raíz del proyecto con las siguientes variables:
  ```env
   DB_NAME=nombre_de_tu_base_de_datos
   DB_USER=tu_usuario
   DB_PASSWORD=tu_contraseña
   DB_HOST=localhost           # Cambia si no estás usando localhost
   DEBUG=True                  # Cambia a False para desactivar el modo debug
  ```
  Estas variables se importarán y utilizarán en el archivo `config.py` para configurar tu proyecto.

### **5. Crear, migrar e insertar datos en la base de datos**:

Puedes hacerlo ejecutando los siguientes scripts:

#### **5.1 Crear la base de datos**

- En Linux/macOS:
  ```bash
   python3 -m app.db.create
  ```
- En Windows:
  ```powershell
   python -m app.db.create
  ```

#### **5.2 Migrar la base de datos**

- En Linux/macOS:
  ```bash
   python3 -m app.db.migrate
  ```
- En Windows:
  ```powershell
   python -m app.db.migrate
  ```

#### **5.3 Insertar datos iniciales**

- En Linux/macOS:
  ```bash
   python3 -m app.db.seed
  ```
- En Windows:
  ```powershell
   python -m app.db.seed
  ```

💡 Alternativamente, puedes usar el script combinado setup.py para hacer todo de una vez:

- En Linux/macOS:
  ```bash
   python3 -m app.db.setup
  ```
- En Windows:
  ```powershell
   python -m app.db.setup
  ```

### 6. **Iniciar la aplicación**:

- En Linux/macOS:
  ```bash
  python3 run.py
  ```
- En Windows:
  ```powershell
  python run.py
  ```

### 7. **Acceder a la aplicación**:

Abre tu navegador y ve a [http://127.0.0.1:5000](http://127.0.0.1:5000).

---

## Aspectos de flujo a notar

- Para agregar usuarios a una sección y asignarle un rol (profesor, ayudante, estudiante) en esa sección, se debe apretar el botón "ver usuarios", y luego abajo está la opción de agregar usuarios. Al agregar este usuario, se le podrá asignar un rol.
- Muchas instancias de objetos no se pueden borrar por diseño de proyecto. Primero se deben borrar manualmente los objetos relacionados.
- Para calificar a los estudiantes, hay que ir a las instancias de las evaluaciones, entrar a una, y en esa página se podrá ver el listado de los estudiantes que corresponden a la sección de la evaluación. En ese mismo listado se permite calificar.

## 🗂 Estructura del Proyecto

La estructura del proyecto es la siguiente:

```
verificable-grupo-8/
├── run.py                     # Punto de entrada principal de la aplicación
├── config.py                  # Configuración de entorno y base de datos
├── requirements.txt           # Lista de dependencias del proyecto
├── README.md                  # Documentación principal
├── app/                       # Lógica principal de la aplicación Flask
│   ├── __init__.py
│   ├── db/                    # Scripts para gestión de la base de datos
│   │   ├── __init__.py
│   │   ├── create.py
│   │   ├── drop.py
│   │   ├── migrate.py
│   │   ├── reset.py
│   │   ├── seed.py
│   │   └── setup.py
│   ├── models/                # Modelos de SQLAlchemy
│   │   ├── __init__.py
│   │   ├── assigned_time_block.py
│   │   ├── classroom.py
│   │   ├── course.py
│   │   ├── course_grade.py
│   │   ├── course_instance.py
│   │   ├── evaluation.py
│   │   ├── evaluation_instance.py
│   │   ├── generate_schedule.py
│   │   ├── requisite.py
│   │   ├── section.py
│   │   ├── student.py
│   │   ├── student_evaluation_instance.py
│   │   ├── student_section.py
│   │   ├── teacher.py
│   │   ├── time_block.py
│   │   └── user.py
│   ├── routes/                # Endpoints de la aplicación
│   │   ├── __init__.py
│   │   ├── auth_routes.py
│   │   ├── course_instance_routes.py
│   │   ├── course_routes.py
│   │   ├── evaluation_instance_routes.py
│   │   ├── evaluation_routes.py
│   │   ├── load_json_routes.py
│   │   ├── main_routes.py
│   │   ├── requisite_routes.py
│   │   ├── section_routes.py
│   │   ├── student_routes.py
│   │   ├── student_section_routes.py
│   │   ├── teacher_routes.py
│   │   └── user_routes.py
│   ├── services/              # Lógica de negocio y validaciones
│   │   ├── __init__.py
│   │   ├── course_service.py
│   │   ├── evaluation_instance_service.py
│   │   ├── schedule_generator.py
│   │   ├── section_service.py
│   │   ├── student_section_service.py
│   │   └── validations.py
│   ├── static/                # Archivos estáticos (CSS, JS, imágenes)
│   └── templates/             # Plantillas HTML con Jinja2
│       ├── base.html
│       ├── auth/
│       ├── course_instances/
│       ├── courses/
│       ├── evaluation_instances/
│       ├── evaluations/
│       ├── load_json/
│       ├── main/
│       ├── partials/
│       ├── sections/
│       ├── student_sections/
│       ├── students/
│       ├── teachers/
│       └── users/
└──
```

---

## 📚 Funcionalidades Principales

### Gestión de Usuarios

- Crear, editar y eliminar usuarios.
- Asignar usuarios a secciones con roles específicos (Estudiante, Ayudante, Profesor).

### Gestión de Cursos

- Crear, editar y eliminar cursos.
- Definir requisitos entre cursos.

### Gestión de Secciones

- Crear secciones asociadas a instancias de cursos.
- Asignar usuarios a secciones.

### Gestión de Evaluaciones

- Crear evaluaciones y asociarlas a secciones.
- Definir ponderaciones y sistemas de evaluación.

### Gestión de Instancias de Evaluaciones

- Crear instancias de evaluaciones (e.g., tareas, pruebas).
- Calificar a los estudiantes en cada instancia.

### Gestión de Horarios

- Asignar bloques de tiempo a secciones y aulas.

---

## 📝 Notas Adicionales

- **Dependencias**: Están especificadas en `requirements.txt`.
- **Base de Datos**: Usa `reset.py` para reiniciar y `seed.py` para cargar datos iniciales.
- **Plantillas**: Las vistas están en la carpeta `templates/` y utilizan Jinja2.
- **Shell interactiva de Flask**:
  - En Linux/macOS:
    ```bash
    python3 -m flask shell
    ```
  - En Windows:
    ```powershell
    python -m flask shell
    ```

---

## ✅ Contribuciones

¡Las contribuciones son bienvenidas! Si encuentras errores o tienes ideas para mejorar la plataforma, no dudes en hacer un pull request o abrir un issue.

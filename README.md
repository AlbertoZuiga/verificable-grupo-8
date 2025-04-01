# Proyecto Verificable - Kanwas

Este repositorio contiene una plataforma educativa desarrollada con Flask. A continuación, se detallan los pasos para configurar el proyecto, su estructura y notas adicionales.

## Configuración del Proyecto

Sigue estos pasos para configurar el entorno y ejecutar la aplicación:

1. **Clonar el repositorio**:

   ```bash
   git clone <URL_DEL_REPOSITORIO>
   cd proyecto-verificable
   ```

2. **Crear un entorno virtual**:

   ```bash
   python3 -m venv venv   # En Windows: python -m venv venv
   source venv/bin/activate  # En Windows: venv\Scripts\activate
   ```

3. **Instalar las dependencias**:

   ```bash
   pip install -r requirements.txt
   ```

4. **Configurar la base de datos**:

   - Asegúrate de tener una base de datos MySQL configurada.
   - Modifica las credenciales en `config.py` según tu entorno.
   - Crea un archivo `.env` en la raíz del proyecto con las siguientes variables:
     ```env
     DB_NAME=nombre_de_tu_base_de_datos
     DB_USER=tu_usuario
     DB_PASSWORD=tu_contraseña
     DB_HOST=localhost  # Cambia si no usas localhost
     ```

5. **Inicializar la base de datos**:

   - Usa el script `reset.py` para eliminar y volver a crear las tablas:
     ```bash
     python app/reset.py
     ```

6. **Insertar datos iniciales**:

   - Usa el script `seed.py` para poblar la base de datos con datos iniciales:
     ```bash
     python app/seed.py
     ```

7. **Iniciar la aplicación**:

   ```bash
   python run.py
   ```

8. **Acceder a la aplicación**:
   Abre tu navegador y ve a [http://127.0.0.1:5000](http://127.0.0.1:5000).

---

## Estructura de Carpetas y Archivos

La estructura del proyecto es la siguiente:

```
proyecto-verificable/
├── run.py                # Archivo principal para iniciar la aplicación Flask.
├── config.py             # Configuración de la base de datos y otras variables.
├── app/                  # Carpeta principal de la aplicación.
│   ├── __init__.py       # Inicialización de la aplicación Flask.
│   ├── models/           # Carpeta con los modelos de la base de datos.
│   │   ├── __init__.py   # Inicialización de modelos.
│   │   ├── course.py     # Modelo del curso.
│   │   ├── course_instance.py # Modelo de instancias de cursos.
│   │   ├── requisite.py  # Modelo de requisitos de cursos.
│   │   ├── section.py    # Modelo de secciones.
│   │   └── user.py       # Modelo de usuarios.
│   ├── routes/           # Carpeta con las rutas de la aplicación.
│   │   ├── __init__.py   # Rutas principales.
│   │   ├── course_routes.py # Rutas relacionadas con los cursos.
│   │   ├── course_instance_routes.py # Rutas relacionadas con instancias de cursos.
│   │   ├── section_routes.py # Rutas relacionadas con secciones.
│   │   └── requisite_routes.py # Rutas relacionadas con requisitos.
│   ├── templates/        # Carpeta con las plantillas HTML.
│   │   ├── base.html     # Plantilla base para la aplicación.
│   │   ├── index.html    # Página de inicio.
│   │   ├── partials/     # Plantillas parciales como el navbar y footer.
│   │   ├── courses/      # Plantillas relacionadas con cursos.
│   │   ├── course_instances/ # Plantillas relacionadas con instancias de cursos.
│   │   └── sections/     # Plantillas relacionadas con secciones.
│   ├── reset.py          # Script para reiniciar la base de datos.
│   ├── seed.py           # Script para insertar datos iniciales en la base de datos.
├── requirements.txt      # Lista de dependencias necesarias para el proyecto.
├── .gitignore            # Archivos y carpetas ignorados por Git.
└── README.md             # Documentación del proyecto.
```

---

## Notas Adicionales

- **Dependencias**: Todas las dependencias necesarias están listadas en `requirements.txt`.
- **Base de Datos**: Usa `reset.py` para reiniciar la base de datos y `seed.py` para poblarla con datos iniciales.
- **Plantillas HTML**: Las plantillas están en la carpeta `templates/` y utilizan Jinja2 para la renderización dinámica.
- **Scripts Útiles**:
  - `python app/reset.py`: Reinicia la base de datos.
  - `python app/seed.py`: Inserta datos iniciales en la base de datos.

¡Disfruta trabajando con este proyecto y no dudes en contribuir!

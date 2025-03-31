# Proyecto Verificable - Plataforma Educativa

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
   pip3 install -r requirements.txt
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

   - Ejecuta el script para crear el esquema de la base de datos:
     ```bash
     python3 seed.py
     ```

6. **Iniciar la aplicación**:

   ```bash
   python3 app.py
   ```

7. **Acceder a la aplicación**:
   Abre tu navegador y ve a [http://127.0.0.1:5000](http://127.0.0.1:5000).

---

## Estructura de Carpetas y Archivos

La estructura del proyecto es la siguiente:

```
proyecto-verificable/
├── app.py                # Archivo principal para iniciar la aplicación Flask.
├── config.py             # Configuración de la base de datos y otras variables.
├── models.py             # Definición de los modelos de la base de datos.
├── routes.py             # Definición de las rutas de la aplicación.
├── seed.py               # Script para insertar datos iniciales en la base de datos.
├── schema.sql            # Archivo para definir el esquema de la base de datos.
├── requirements.txt      # Lista de dependencias necesarias para el proyecto.
├── .gitignore            # Archivos y carpetas ignorados por Git.
├── templates/            # Carpeta con las plantillas HTML.
│   ├── base.html         # Plantilla base para la aplicación.
│   ├── index.html        # Página de inicio.
│   └── courses.html      # Página para listar los cursos.
└── README.md             # Documentación del proyecto.
```

---

## Notas Adicionales

- **Dependencias**: Todas las dependencias necesarias están listadas en `requirements.txt`.
- **Base de Datos**: Asegúrate de que la base de datos esté configurada correctamente antes de ejecutar la aplicación.
- **Plantillas HTML**: Las plantillas están en la carpeta `templates/` y utilizan Jinja2 para la renderización dinámica.
- **Scripts Útiles**: Usa `seed.py` para inicializar datos en la base de datos.

¡Disfruta trabajando con este proyecto y no dudes en contribuir!

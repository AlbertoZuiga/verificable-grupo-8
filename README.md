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

  - Asegúrate de MySQL instalado y configurado en tu dispositivo.
  - Crea un archivo `.env` en la raíz del proyecto con las siguientes variables:
    ```env
     DB_NAME=nombre_de_tu_base_de_datos
     DB_USER=tu_usuario
     DB_PASSWORD=tu_contraseña
     DB_HOST=localhost           # Cambia si no estás usando localhost
     DEBUG=True                  # Cambia a False para desactivar el modo debug
    ```
  Estas variables se importaran y utilizaran en el archivo `config.py` para configurar tu proyecto.

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
│   │   ├── course.py
│   │   ├── course_instance.py
│   │   ├── evaluation.py
│   │   ├── evaluation_instance.py
│   │   ├── requisite.py
│   │   ├── section.py
│   │   └── user.py
│   ├── routes/                # Endpoints de la aplicación
│   │   ├── __init__.py
│   │   ├── auth_routes.py
│   │   ├── main_routes.py
│   │   ├── course_routes.py
│   │   ├── course_instance_routes.py
│   │   ├── section_routes.py
│   │   ├── requisite_routes.py
│   │   ├── evaluation_routes.py
│   │   └── evaluation_instance_routes.py
│   ├── static/                # Archivos estáticos (CSS, JS, imágenes)
│   └── templates/             # Plantillas HTML con Jinja2
│       ├── base.html
│       ├── auth/
│       ├── main/
│       ├── partials/
│       ├── courses/
│       ├── course_instances/
│       ├── sections/
│       ├── evaluations/
│       └── evaluation_instances/
└── 
```

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
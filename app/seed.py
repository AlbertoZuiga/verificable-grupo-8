import sys
import os

# Agregar el directorio raíz al PYTHONPATH para encontrar 'app'
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app, db  # ✅ Importa create_app y db correctamente
from app.models.course import Course

def seed_data():
    """ Inserta datos en la base de datos si no existen. """
    app = create_app()  # ✅ Crear la instancia de la app
    with app.app_context():  # ✅ Asegurar que estamos dentro del contexto de la app
        try:
            if Course.query.first():  # Verifica si ya hay datos
                print("📌 Datos ya existen. No se agregaron duplicados.")
                return

            courses = [
                Course(title="Desarrollo de Software Verificable"),
                Course(title="Almacenamiento y Procesamiento Masivo de Datos"),
                Course(title="Software Design"),
            ]

            db.session.add_all(courses)
            db.session.commit()

            print("✅ Seed ejecutado correctamente.")

        except Exception as e:
            db.session.rollback()
            print(f"❌ Error al ejecutar seed: {e}")

if __name__ == "__main__":
    seed_data()

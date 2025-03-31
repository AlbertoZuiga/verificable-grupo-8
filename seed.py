from app import create_app
from models import db, Course

def seed_data():
    """ Inserta datos en la base de datos si no existen. """
    app = create_app()  # Crear la instancia de la app
    with app.app_context():
        try:
            if Course.query.first():
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

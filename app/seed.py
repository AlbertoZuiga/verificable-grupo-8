from app import create_app, db  # Importa la función para crear la app
from app.models.course import Course
from app.models.course_instance import CourseInstance, SemesterEnum

def seed_data():
    print("Seeding database...")

    # Crear cursos de ejemplo
    courses_data = [
        {"title": "Matemáticas Avanzadas"},
        {"title": "Programación en Python"},
        {"title": "Historia Universal"}
    ]

    courses = []
    for data in courses_data:
        course = Course.query.filter_by(title=data["title"]).first()
        if not course:
            course = Course(title=data["title"], description=data["description"])
            db.session.add(course)
        else:
            print(f"El curso '{data['title']}' ya existe, no se añadirá de nuevo.")
        
        courses.append(course)

    db.session.commit()  # Guardar todos los cursos antes de crear instancias

    if len(courses) < 3:
        print("Error: No se pudieron obtener todos los cursos correctamente.")
        return

    # Crear instancias de cursos
    instances = [
        CourseInstance(course_id=courses[0].id, year=2024, semester=1),
        CourseInstance(course_id=courses[0].id, year=2024, semester=2),
        CourseInstance(course_id=courses[1].id, year=2024, semester=1),
        CourseInstance(course_id=courses[2].id, year=2023, semester=2),
    ]

    db.session.add_all(instances)
    db.session.commit()

    print("Seeding completed!")

if __name__ == "__main__":
    app = create_app()  # Inicializar la aplicación Flask correctamente
    with app.app_context():  # Asegurar el contexto de la aplicación
        seed_data()

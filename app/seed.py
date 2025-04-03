from app import create_app, db
from app.models.course import Course
from app.models.course_instance import CourseInstance, SemesterEnum
from app.models.section import Section, WeightingType
from app.models.requisite import Requisite
from app.models.user import User
from app.models.evaluation import Evaluation

def seed_data():
    print("Seeding database...")

    users_data = [
        {"first_name": "Juan", "last_name": "Pérez", "email": "juan.perez@example.com", "university_entry_date": "2020-01-15"},
        {"first_name": "María", "last_name": "González", "email": "maria.gonzalez@example.com", "university_entry_date": "2019-08-20"},
        {"first_name": "Carlos", "last_name": "Ramírez", "email": "carlos.ramirez@example.com", "university_entry_date": "2021-03-10"},
        {"first_name": "Ana", "last_name": "López", "email": "ana.lopez@example.com", "university_entry_date": "2022-09-05"},
        {"first_name": "Luis", "last_name": "Martínez", "email": "luis.martinez@example.com", "university_entry_date": "2020-07-01"},
    ]

    for data in users_data:
        user = User.query.filter_by(email=data["email"]).first()
        if not user:
            user = User(
                first_name=data["first_name"],
                last_name=data["last_name"],
                email=data["email"],
                university_entry_date=data["university_entry_date"]
            )
            db.session.add(user)
        else:
            print(f"El usuario con email '{data['email']}' ya existe, no se añadirá de nuevo.")

    db.session.commit()

    courses_data = [
        {"title": "Matemáticas Avanzadas"},
        {"title": "Programación en Python"},
        {"title": "Historia Universal"},
        {"title": "Física Cuántica"},
        {"title": "Inteligencia Artificial"},
        {"title": "Química Orgánica"},
        {"title": "Literatura Clásica"},
        {"title": "Diseño de Software"},
        {"title": "Economía Global"},
        {"title": "Biología Molecular"}
    ]

    courses = []
    for data in courses_data:
        course = Course.query.filter_by(title=data["title"]).first()
        if not course:
            course = Course(title=data["title"])
            db.session.add(course)
        else:
            print(f"El curso '{data['title']}' ya existe, no se añadirá de nuevo.")
        
        courses.append(course)

    db.session.commit()

    if len(courses) < len(courses_data):
        print("Error: No se pudieron obtener todos los cursos correctamente.")
        return

    instances = [
        CourseInstance(course_id=courses[0].id, year=2024, semester=1),
        CourseInstance(course_id=courses[1].id, year=2024, semester=1),
        CourseInstance(course_id=courses[2].id, year=2023, semester=2),
        CourseInstance(course_id=courses[3].id, year=2024, semester=2),
        CourseInstance(course_id=courses[4].id, year=2023, semester=1),
        CourseInstance(course_id=courses[5].id, year=2023, semester=2),
        CourseInstance(course_id=courses[6].id, year=2024, semester=1),
        CourseInstance(course_id=courses[7].id, year=2024, semester=2),
        CourseInstance(course_id=courses[8].id, year=2023, semester=1),
        CourseInstance(course_id=courses[9].id, year=2023, semester=2),
    ]

    db.session.add_all(instances)
    db.session.commit()

    sections = [
        Section(course_instance_id=instances[0].id, code=101, weighting_type=WeightingType.PERCENTAGE),
        Section(course_instance_id=instances[1].id, code=102, weighting_type=WeightingType.WEIGHTS),
        Section(course_instance_id=instances[2].id, code=201, weighting_type=WeightingType.PERCENTAGE),
        Section(course_instance_id=instances[3].id, code=301, weighting_type=WeightingType.WEIGHTS),
        Section(course_instance_id=instances[4].id, code=401, weighting_type=WeightingType.PERCENTAGE),
        Section(course_instance_id=instances[5].id, code=501, weighting_type=WeightingType.WEIGHTS),
        Section(course_instance_id=instances[6].id, code=601, weighting_type=WeightingType.PERCENTAGE),
        Section(course_instance_id=instances[7].id, code=701, weighting_type=WeightingType.WEIGHTS),
        Section(course_instance_id=instances[8].id, code=801, weighting_type=WeightingType.PERCENTAGE),
        Section(course_instance_id=instances[9].id, code=901, weighting_type=WeightingType.WEIGHTS),
    ]

    db.session.add_all(sections)
    db.session.commit()

    requisites = [
        Requisite(course_id=courses[0].id, course_requisite_id=courses[1].id),
        Requisite(course_id=courses[1].id, course_requisite_id=courses[2].id),
        Requisite(course_id=courses[3].id, course_requisite_id=courses[4].id),
        Requisite(course_id=courses[5].id, course_requisite_id=courses[6].id),
        Requisite(course_id=courses[7].id, course_requisite_id=courses[8].id),
    ]

    db.session.add_all(requisites)
    db.session.commit()

    evaluations = [
        Evaluation(section_id=sections[0].id, title="Examen", weight=30, weighting_system=WeightingType.PERCENTAGE),
        Evaluation(section_id=sections[0].id, title="Tareas", weight=20, weighting_system=WeightingType.PERCENTAGE),
        Evaluation(section_id=sections[1].id, title="Proyecto", weight=50, weighting_system=WeightingType.WEIGHTS),
        Evaluation(section_id=sections[1].id, title="Examen", weight=50, weighting_system=WeightingType.WEIGHTS),
        Evaluation(section_id=sections[2].id, title="Examen", weight=40, weighting_system=WeightingType.PERCENTAGE),
        Evaluation(section_id=sections[2].id, title="Tareas", weight=60, weighting_system=WeightingType.PERCENTAGE),
    ]

    db.session.add_all(evaluations)
    db.session.commit()


    print("Seeding completed!")

if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        seed_data()

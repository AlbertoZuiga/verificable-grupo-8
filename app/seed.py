import random
from app import create_app, db
from app.models.course import Course
from app.models.course_instance import CourseInstance, Semester
from app.models.section import Section, WeighingType
from app.models.requisite import Requisite
from app.models.user import User
from app.models.evaluation import Evaluation
from app.models.evaluation_instance import EvaluationInstance

def seed_data():
    print("Seeding database...")

    users_data = [
        {"first_name": "Juan", "last_name": "Pérez", "email": "juan.perez@example.com", "university_entry_date": "2020-01-15"},
        {"first_name": "María", "last_name": "González", "email": "maria.gonzalez@example.com", "university_entry_date": "2019-08-20"},
        {"first_name": "Carlos", "last_name": "Ramírez", "email": "carlos.ramirez@example.com", "university_entry_date": "2021-03-10"},
        {"first_name": "Ana", "last_name": "López", "email": "ana.lopez@example.com", "university_entry_date": "2022-09-05"},
        {"first_name": "Luis", "last_name": "Martínez", "email": "luis.martinez@example.com", "university_entry_date": "2020-07-01"},
    ]

    for user_data in users_data:
        user = User.query.filter_by(email=user_data["email"]).first()
        if not user:
            user = User(
                first_name=user_data["first_name"],
                last_name=user_data["last_name"],
                email=user_data["email"],
                university_entry_date=user_data["university_entry_date"]
            )
            db.session.add(user)
        else:
            print(f"El usuario con email '{user_data['email']}' ya existe, no se añadirá de nuevo.")

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
    for course_data in courses_data:
        course = Course.query.filter_by(title=course_data["title"]).first()
        if not course:
            course = Course(title=course_data["title"])
            db.session.add(course)
        else:
            print(f"El curso '{course_data['title']}' ya existe, no se añadirá de nuevo.")
        
        courses.append(course)

    db.session.commit()

    if len(courses) < len(courses_data):
        print("Error: No se pudieron obtener todos los cursos correctamente.")
        return

    for course in courses:
        for i in range(random.randint(1, 5)):
            course_instance = CourseInstance(
                course_id=course.id,
                year=random.randint(2015, 2025),
                semester=random.choice([Semester.FIRST, Semester.SECOND])
            )
            db.session.add(course_instance)

    db.session.commit()
    
    course_instances = CourseInstance.query.all()
    for instance in course_instances:
        for i in range(random.randint(1, 3)):
            unique_code = False
            while not unique_code:
                code = random.randint(100, 999)
                if not Section.query.filter_by(code=code).first():
                    unique_code = True
            section = Section(course_instance_id=instance.id, code=code, weighing_type=random.choice([WeighingType.PERCENTAGE, WeighingType.WEIGHT]))
            db.session.add(section)

    db.session.commit()

    for course in courses:
        possible_prerequisites = [c for c in courses if c.id != course.id]
        num_prerequisites = random.randint(1, min(3, len(possible_prerequisites)))

        selected_prerequisites = random.sample(possible_prerequisites, num_prerequisites)
        for prerequisite in selected_prerequisites:
            if not Requisite.query.filter_by(course_id=course.id, course_requisite_id=prerequisite.id).first():
                requisite = Requisite(course_id=course.id, course_requisite_id=prerequisite.id)
                db.session.add(requisite)
    db.session.commit()

    evaluations = ["Tareas", "Proyecto", "Controles", "Pruebas"]
    sections = Section.query.all()
    for section in sections:
        selected_evaluations = random.sample(evaluations, 2)
        for title in selected_evaluations:
            evaluation = Evaluation(
                section_id=section.id,
                title=title,
                weighing=random.randint(10, 50),
                weighing_system=random.choice([WeighingType.PERCENTAGE, WeighingType.WEIGHT])
            )
            db.session.add(evaluation)
        
        evaluation = Evaluation(section_id=section.id, title="Examen", weighing=30, weighing_system=WeighingType.WEIGHT)
        db.session.add(evaluation)
    db.session.commit()
    
    evaluations = Evaluation.query.where(Evaluation.title != "Examen").all()
    for evaluation in evaluations:
        for i in range(random.randint(2, 7)):
            evaluation_instance = EvaluationInstance(title=f'{evaluation.title} {i+1}', instance_weighing=random.randint(10, 50), optional=False, evaluation_id=evaluation.id)
            db.session.add(evaluation_instance)
    db.session.commit()
            
    exams = Evaluation.query.where(Evaluation.title == "Examen").all()
    for exam in exams:
        evaluation_instance = EvaluationInstance(title=exam.title, instance_weighing=1, optional=False, evaluation_id=evaluation.id)
        db.session.add(evaluation_instance)

    db.session.commit()    

    print("Seeding completed!")

if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        seed_data()

import random
from app import app, kanvas_db
from app.models.course import Course
from app.models.course_instance import CourseInstance, Semester
from app.models.section import Section, WeighingType
from app.models.requisite import Requisite
from app.models.user import User
from app.models.evaluation import Evaluation
from app.models.evaluation_instance import EvaluationInstance
from app.models.user_section import UserSection, SectionRole

def seed_database():
    print("Creando datos...")

    users_data = [
        {"first_name": "Juan", "last_name": "Pérez", "email": "juan.perez@example.com", "password": "password", "university_entry_year": 2020},
        {"first_name": "María", "last_name": "González", "email": "maria.gonzalez@example.com", "password": "password", "university_entry_year": 2019},
        {"first_name": "Carlos", "last_name": "Ramírez", "email": "carlos.ramirez@example.com", "password": "password", "university_entry_year": 2021},
        {"first_name": "Ana", "last_name": "López", "email": "ana.lopez@example.com", "password": "password", "university_entry_year": 2022},
        {"first_name": "Luis", "last_name": "Martínez", "email": "luis.martinez@example.com", "password": "password", "university_entry_year": 2020},
        {"first_name": "Sofía", "last_name": "Hernández", "email": "sofia.hernandez@example.com", "password": "password", "university_entry_year": 2023},
        {"first_name": "Diego", "last_name": "Castro", "email": "diego.castro@example.com", "password": "password", "university_entry_year": 2021},
        {"first_name": "Valentina", "last_name": "Torres", "email": "valentina.torres@example.com", "password": "password", "university_entry_year": 2022},
        {"first_name": "Andrés", "last_name": "Ruiz", "email": "andres.ruiz@example.com", "password": "password", "university_entry_year": 2019},
        {"first_name": "Camila", "last_name": "Flores", "email": "camila.flores@example.com", "password": "password", "university_entry_year": 2020},
        {"first_name": "Mateo", "last_name": "Vargas", "email": "mateo.vargas@example.com", "password": "password", "university_entry_year": 2021},
        {"first_name": "Isabella", "last_name": "Cruz", "email": "isabella.cruz@example.com", "password": "password", "university_entry_year": 2023},
        {"first_name": "Gabriel", "last_name": "Mendoza", "email": "gabriel.mendoza@example.com", "password": "password", "university_entry_year": 2022},
        {"first_name": "Renata", "last_name": "Sánchez", "email": "renata.sanchez@example.com", "password": "password", "university_entry_year": 2020},
        {"first_name": "Sebastián", "last_name": "Ríos", "email": "sebastian.rios@example.com", "password": "password", "university_entry_year": 2021},
        {"first_name": "Daniela", "last_name": "Romero", "email": "daniela.romero@example.com", "password": "password", "university_entry_year": 2023},
        {"first_name": "Tomás", "last_name": "Navarro", "email": "tomas.navarro@example.com", "password": "password", "university_entry_year": 2019},
        {"first_name": "Lucía", "last_name": "Delgado", "email": "lucia.delgado@example.com", "password": "password", "university_entry_year": 2021},
        {"first_name": "Martín", "last_name": "Ortega", "email": "martin.ortega@example.com", "password": "password", "university_entry_year": 2022},
        {"first_name": "Paula", "last_name": "Guerrero", "email": "paula.guerrero@example.com", "password": "password", "university_entry_year": 2020},
        {"first_name": "Emilio", "last_name": "Peña", "email": "emilio.pena@example.com", "password": "password", "university_entry_year": 2018},
        {"first_name": "Florencia", "last_name": "Cabrera", "email": "florencia.cabrera@example.com", "password": "password", "university_entry_year": 2023},
        {"first_name": "Santiago", "last_name": "Silva", "email": "santiago.silva@example.com", "password": "password", "university_entry_year": 2022},
        {"first_name": "Regina", "last_name": "Aguilar", "email": "regina.aguilar@example.com", "password": "password", "university_entry_year": 2020},
        {"first_name": "Joaquín", "last_name": "Ramos", "email": "joaquin.ramos@example.com", "password": "password", "university_entry_year": 2021},
        {"first_name": "Natalia", "last_name": "Morales", "email": "natalia.morales@example.com", "password": "password", "university_entry_year": 2023},
        {"first_name": "Agustín", "last_name": "León", "email": "agustin.leon@example.com", "password": "password", "university_entry_year": 2022},
        {"first_name": "Julieta", "last_name": "Reyes", "email": "julieta.reyes@example.com", "password": "password", "university_entry_year": 2019},
        {"first_name": "Bruno", "last_name": "Campos", "email": "bruno.campos@example.com", "password": "password", "university_entry_year": 2021},
        {"first_name": "Ariana", "last_name": "Mora", "email": "ariana.mora@example.com", "password": "password", "university_entry_year": 2022},
        {"first_name": "Lucas", "last_name": "Herrera", "email": "lucas.herrera@example.com", "password": "password", "university_entry_year": 2020},
        {"first_name": "Fernanda", "last_name": "Rojas", "email": "fernanda.rojas@example.com", "password": "password", "university_entry_year": 2021},
        {"first_name": "Iván", "last_name": "Núñez", "email": "ivan.nunez@example.com", "password": "password", "university_entry_year": 2023},
        {"first_name": "Antonia", "last_name": "Paredes", "email": "antonia.paredes@example.com", "password": "password", "university_entry_year": 2018},
        {"first_name": "Benjamín", "last_name": "Luna", "email": "benjamin.luna@example.com", "password": "password", "university_entry_year": 2020},
        {"first_name": "Emma", "last_name": "Cordero", "email": "emma.cordero@example.com", "password": "password", "university_entry_year": 2022},
        {"first_name": "Maximiliano", "last_name": "Figueroa", "email": "maximiliano.figueroa@example.com", "password": "password", "university_entry_year": 2021},
        {"first_name": "Bianca", "last_name": "Carrillo", "email": "bianca.carrillo@example.com", "password": "password", "university_entry_year": 2023},
        {"first_name": "Franco", "last_name": "Salazar", "email": "franco.salazar@example.com", "password": "password", "university_entry_year": 2020},
        {"first_name": "Elena", "last_name": "Soto", "email": "elena.soto@example.com", "password": "password", "university_entry_year": 2021},
        {"first_name": "Alan", "last_name": "Arias", "email": "alan.arias@example.com", "password": "password", "university_entry_year": 2022},
        {"first_name": "Josefina", "last_name": "Mejía", "email": "josefina.mejia@example.com", "password": "password", "university_entry_year": 2020},
        {"first_name": "Facundo", "last_name": "Escobar", "email": "facundo.escobar@example.com", "password": "password", "university_entry_year": 2021},
        {"first_name": "Clara", "last_name": "Acosta", "email": "clara.acosta@example.com", "password": "password", "university_entry_year": 2023},
        {"first_name": "Leonardo", "last_name": "Ibarra", "email": "leonardo.ibarra@example.com", "password": "password", "university_entry_year": 2022},
        {"first_name": "Catalina", "last_name": "Valenzuela", "email": "catalina.valenzuela@example.com", "password": "password", "university_entry_year": 2019},
        {"first_name": "Hugo", "last_name": "Saavedra", "email": "hugo.saavedra@example.com", "password": "password", "university_entry_year": 2021},
        {"first_name": "Milagros", "last_name": "Zamora", "email": "milagros.zamora@example.com", "password": "password", "university_entry_year": 2020},
        {"first_name": "Axel", "last_name": "Vergara", "email": "axel.vergara@example.com", "password": "password", "university_entry_year": 2023},
        {"first_name": "Martina", "last_name": "Pizarro", "email": "martina.pizarro@example.com", "password": "password", "university_entry_year": 2022},
        {"first_name": "Cristóbal", "last_name": "Fuentes", "email": "cristobal.fuentes@example.com", "password": "password", "university_entry_year": 2019},
        {"first_name": "Josefa", "last_name": "Godoy", "email": "josefa.godoy@example.com", "password": "password", "university_entry_year": 2021},
        {"first_name": "Gael", "last_name": "Montoya", "email": "gael.montoya@example.com", "password": "password", "university_entry_year": 2020},
        {"first_name": "Alma", "last_name": "Esquivel", "email": "alma.esquivel@example.com", "password": "password", "university_entry_year": 2022},
        {"first_name": "Enzo", "last_name": "Tapia", "email": "enzo.tapia@example.com", "password": "password", "university_entry_year": 2023},
    ]

    for user_data in users_data:
        user = User.query.filter_by(email=user_data["email"]).first()
        if not user:
            user = User(
                first_name=user_data["first_name"],
                last_name=user_data["last_name"],
                email=user_data["email"],
                university_entry_year=user_data["university_entry_year"]
            )
            user.set_password(user_data["password"])
            kanvas_db.session.add(user)

    kanvas_db.session.commit()

    courses_data = [
        {"title": "Matemáticas Avanzadas", "code": "MA101", "credits": 5},
        {"title": "Programación en Python", "code": "PY101", "credits": 5},
        {"title": "Historia Universal", "code": "HU101", "credits": 4},
        {"title": "Física Cuántica", "code": "FQ101", "credits": 6},
        {"title": "Inteligencia Artificial", "code": "IA101", "credits": 5},
        {"title": "Química Orgánica", "code": "QO101", "credits": 6},
        {"title": "Literatura Clásica", "code": "LC101", "credits": 4},
        {"title": "Diseño de Software", "code": "DS101", "credits": 5},
        {"title": "Economía Global", "code": "EG101", "credits": 4},
        {"title": "Biología Molecular", "code": "BM101", "credits": 5}
    ]



    courses = []
    for course_data in courses_data:
        course = Course.query.filter_by(title=course_data["title"]).first()
        if not course:
            # Aquí asignamos el código y los créditos al crear el curso
            course = Course(
                title=course_data["title"], 
                code=course_data["code"], 
                credits=course_data["credits"]
            )
            kanvas_db.session.add(course)
        else:
            print(f"\tEl curso '{course_data['title']}' ya existe, no se añadirá de nuevo.")
        
        courses.append(course)

    kanvas_db.session.commit()

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
            kanvas_db.session.add(course_instance)

    kanvas_db.session.commit()
    
    course_instances = CourseInstance.query.all()
    for instance in course_instances:
        for i in range(random.randint(1, 3)):
            unique_code = False
            while not unique_code:
                code = random.randint(100, 999)
                if not Section.query.filter_by(code=code).first():
                    unique_code = True
            section = Section(course_instance_id=instance.id, code=code, weighing_type=random.choice([WeighingType.PERCENTAGE, WeighingType.WEIGHT]))
            kanvas_db.session.add(section)

    kanvas_db.session.commit()

    for course in courses:
        possible_prerequisites = [c for c in courses if c.id != course.id]
        num_prerequisites = random.randint(1, min(3, len(possible_prerequisites)))

        selected_prerequisites = random.sample(possible_prerequisites, num_prerequisites)
        for prerequisite in selected_prerequisites:
            if not Requisite.query.filter_by(course_id=course.id, course_requisite_id=prerequisite.id).first():
                requisite = Requisite(course_id=course.id, course_requisite_id=prerequisite.id)
                kanvas_db.session.add(requisite)
    kanvas_db.session.commit()

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
            kanvas_db.session.add(evaluation)
        
        evaluation = Evaluation(section_id=section.id, title="Examen", weighing=30, weighing_system=WeighingType.WEIGHT)
        kanvas_db.session.add(evaluation)
        
        students = random.sample(User.query.all(), random.randint(19, 29))

        teacher = random.choice(students)
        students.remove(teacher)

        user_section = UserSection(user_id=teacher.id, section_id=section.id, role=SectionRole.TEACHER)
        kanvas_db.session.add(user_section)

        assistants = random.sample(students, 3)
        for assistant in assistants:
            students.remove(assistant)
            user_section = UserSection(user_id=assistant.id, section_id=section.id, role=SectionRole.ASSISTANT)
            kanvas_db.session.add(user_section)
        
        for student in students:
            user_section = UserSection(user_id=student.id, section_id=section.id, role=SectionRole.STUDENT)
            kanvas_db.session.add(user_section)

    kanvas_db.session.commit()
    
    singular_evaluations = {"Tareas":"Tarea", "Proyecto":"Proyecto", "Controles":"Control", "Pruebas":"Prueba"}
    evaluations = Evaluation.query.where(Evaluation.title != "Examen").all()
    for evaluation in evaluations:
        for i in range(random.randint(2, 7)):
            evaluation_instance = EvaluationInstance(title=f'{singular_evaluations[evaluation.title]} {i+1}', instance_weighing=random.randint(10, 50), optional=False, evaluation_id=evaluation.id)
            kanvas_db.session.add(evaluation_instance)
    kanvas_db.session.commit()
            
    exams = Evaluation.query.where(Evaluation.title == "Examen").all()
    for exam in exams:
        evaluation_instance = EvaluationInstance(title=exam.title, instance_weighing=1, optional=False, evaluation_id=evaluation.id)
        kanvas_db.session.add(evaluation_instance)

    kanvas_db.session.commit()    

    print("Datos creados correctamente!")

if __name__ == "__main__":
    with app.app_context():
        seed_database()

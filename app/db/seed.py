import random

from app import kanvas_app, kanvas_db
from app.models import (
    Course,
    CourseInstance,
    Requisite,
    Section,
    Semester,
    Teacher,
    User,
    WeighingType,
)


def seed_database():
    print("Creando datos...\n\n")

    print("Creando usuarios...")
    users_data = [
        {
            "first_name": "Juan",
            "last_name": "Pérez",
            "email": "juan.perez@example.com",
            "password": "password",
        },
        {
            "first_name": "María",
            "last_name": "González",
            "email": "maria.gonzalez@example.com",
            "password": "password",
        },
        {
            "first_name": "Carlos",
            "last_name": "Ramírez",
            "email": "carlos.ramirez@example.com",
            "password": "password",
        },
        {
            "first_name": "Ana",
            "last_name": "López",
            "email": "ana.lopez@example.com",
            "password": "password",
        },
        {
            "first_name": "Luis",
            "last_name": "Martínez",
            "email": "luis.martinez@example.com",
            "password": "password",
        },
        {
            "first_name": "Sofía",
            "last_name": "Hernández",
            "email": "sofia.hernandez@example.com",
            "password": "password",
        },
        {
            "first_name": "Diego",
            "last_name": "Castro",
            "email": "diego.castro@example.com",
            "password": "password",
        },
        {
            "first_name": "Valentina",
            "last_name": "Torres",
            "email": "valentina.torres@example.com",
            "password": "password",
        },
        {
            "first_name": "Andrés",
            "last_name": "Ruiz",
            "email": "andres.ruiz@example.com",
            "password": "password",
        },
        {
            "first_name": "Camila",
            "last_name": "Flores",
            "email": "camila.flores@example.com",
            "password": "password",
        },
        {
            "first_name": "Mateo",
            "last_name": "Vargas",
            "email": "mateo.vargas@example.com",
            "password": "password",
        },
        {
            "first_name": "Isabella",
            "last_name": "Cruz",
            "email": "isabella.cruz@example.com",
            "password": "password",
        },
        {
            "first_name": "Gabriel",
            "last_name": "Mendoza",
            "email": "gabriel.mendoza@example.com",
            "password": "password",
        },
        {
            "first_name": "Renata",
            "last_name": "Sánchez",
            "email": "renata.sanchez@example.com",
            "password": "password",
        },
        {
            "first_name": "Sebastián",
            "last_name": "Ríos",
            "email": "sebastian.rios@example.com",
            "password": "password",
        },
        {
            "first_name": "Daniela",
            "last_name": "Romero",
            "email": "daniela.romero@example.com",
            "password": "password",
        },
        {
            "first_name": "Tomás",
            "last_name": "Navarro",
            "email": "tomas.navarro@example.com",
            "password": "password",
        },
        {
            "first_name": "Lucía",
            "last_name": "Delgado",
            "email": "lucia.delgado@example.com",
            "password": "password",
        },
        {
            "first_name": "Martín",
            "last_name": "Ortega",
            "email": "martin.ortega@example.com",
            "password": "password",
        },
        {
            "first_name": "Paula",
            "last_name": "Guerrero",
            "email": "paula.guerrero@example.com",
            "password": "password",
        },
        {
            "first_name": "Emilio",
            "last_name": "Peña",
            "email": "emilio.pena@example.com",
            "password": "password",
        },
        {
            "first_name": "Florencia",
            "last_name": "Cabrera",
            "email": "florencia.cabrera@example.com",
            "password": "password",
        },
        {
            "first_name": "Santiago",
            "last_name": "Silva",
            "email": "santiago.silva@example.com",
            "password": "password",
        },
        {
            "first_name": "Regina",
            "last_name": "Aguilar",
            "email": "regina.aguilar@example.com",
            "password": "password",
        },
        {
            "first_name": "Joaquín",
            "last_name": "Ramos",
            "email": "joaquin.ramos@example.com",
            "password": "password",
        },
        {
            "first_name": "Natalia",
            "last_name": "Morales",
            "email": "natalia.morales@example.com",
            "password": "password",
        },
        {
            "first_name": "Agustín",
            "last_name": "León",
            "email": "agustin.leon@example.com",
            "password": "password",
        },
        {
            "first_name": "Julieta",
            "last_name": "Reyes",
            "email": "julieta.reyes@example.com",
            "password": "password",
        },
        {
            "first_name": "Bruno",
            "last_name": "Campos",
            "email": "bruno.campos@example.com",
            "password": "password",
        },
        {
            "first_name": "Ariana",
            "last_name": "Mora",
            "email": "ariana.mora@example.com",
            "password": "password",
        },
        {
            "first_name": "Lucas",
            "last_name": "Herrera",
            "email": "lucas.herrera@example.com",
            "password": "password",
        },
        {
            "first_name": "Fernanda",
            "last_name": "Rojas",
            "email": "fernanda.rojas@example.com",
            "password": "password",
        },
        {
            "first_name": "Iván",
            "last_name": "Núñez",
            "email": "ivan.nunez@example.com",
            "password": "password",
        },
        {
            "first_name": "Antonia",
            "last_name": "Paredes",
            "email": "antonia.paredes@example.com",
            "password": "password",
        },
        {
            "first_name": "Benjamín",
            "last_name": "Luna",
            "email": "benjamin.luna@example.com",
            "password": "password",
        },
        {
            "first_name": "Emma",
            "last_name": "Cordero",
            "email": "emma.cordero@example.com",
            "password": "password",
        },
        {
            "first_name": "Maximiliano",
            "last_name": "Figueroa",
            "email": "maximiliano.figueroa@example.com",
            "password": "password",
        },
        {
            "first_name": "Bianca",
            "last_name": "Carrillo",
            "email": "bianca.carrillo@example.com",
            "password": "password",
        },
        {
            "first_name": "Franco",
            "last_name": "Salazar",
            "email": "franco.salazar@example.com",
            "password": "password",
        },
        {
            "first_name": "Elena",
            "last_name": "Soto",
            "email": "elena.soto@example.com",
            "password": "password",
        },
        {
            "first_name": "Alan",
            "last_name": "Arias",
            "email": "alan.arias@example.com",
            "password": "password",
        },
        {
            "first_name": "Josefina",
            "last_name": "Mejía",
            "email": "josefina.mejia@example.com",
            "password": "password",
        },
        {
            "first_name": "Facundo",
            "last_name": "Escobar",
            "email": "facundo.escobar@example.com",
            "password": "password",
        },
        {
            "first_name": "Clara",
            "last_name": "Acosta",
            "email": "clara.acosta@example.com",
            "password": "password",
        },
        {
            "first_name": "Leonardo",
            "last_name": "Ibarra",
            "email": "leonardo.ibarra@example.com",
            "password": "password",
        },
        {
            "first_name": "Catalina",
            "last_name": "Valenzuela",
            "email": "catalina.valenzuela@example.com",
            "password": "password",
        },
        {
            "first_name": "Hugo",
            "last_name": "Saavedra",
            "email": "hugo.saavedra@example.com",
            "password": "password",
        },
        {
            "first_name": "Milagros",
            "last_name": "Zamora",
            "email": "milagros.zamora@example.com",
            "password": "password",
        },
        {
            "first_name": "Axel",
            "last_name": "Vergara",
            "email": "axel.vergara@example.com",
            "password": "password",
        },
        {
            "first_name": "Martina",
            "last_name": "Pizarro",
            "email": "martina.pizarro@example.com",
            "password": "password",
        },
        {
            "first_name": "Cristóbal",
            "last_name": "Fuentes",
            "email": "cristobal.fuentes@example.com",
            "password": "password",
        },
        {
            "first_name": "Josefa",
            "last_name": "Godoy",
            "email": "josefa.godoy@example.com",
            "password": "password",
        },
        {
            "first_name": "Gael",
            "last_name": "Montoya",
            "email": "gael.montoya@example.com",
            "password": "password",
        },
        {
            "first_name": "Alma",
            "last_name": "Esquivel",
            "email": "alma.esquivel@example.com",
            "password": "password",
        },
        {
            "first_name": "Enzo",
            "last_name": "Tapia",
            "email": "enzo.tapia@example.com",
            "password": "password",
        },
    ]

    for user_data in users_data:
        user = User.query.filter_by(email=user_data["email"]).first()
        if not user:
            user = User(
                first_name=user_data["first_name"],
                last_name=user_data["last_name"],
                email=user_data["email"],
            )
            user.set_password(user_data["password"])
            kanvas_db.session.add(user)

    kanvas_db.session.commit()
    print("Usuarios creados correctamente!\n")

    print("Creando profesores...")
    users = User.query.all()
    teachers = random.sample(users, 10)
    teacher_ids = {user.id for user in teachers}
    for user in teachers:
        teacher = Teacher.query.filter_by(user_id=user.id).first()

        if not teacher:
            teacher = Teacher(user_id=user.id)

            kanvas_db.session.add(teacher)

    kanvas_db.session.commit()
    print("Profesores creados correctamente!\n")

    print("Creando alumnos...")
    students = [user for user in users if user.id not in teacher_ids]
    from app.models import Student

    for user in students:
        student = Student.query.filter_by(user_id=user.id).first()

        if not student:
            student = Student(user_id=user.id, university_entry_year=random.randint(2015, 2025))

            kanvas_db.session.add(student)
    print("Alumnos creados correctamente!\n")

    print("Creando cursos y secciones...")
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
        {"title": "Biología Molecular", "code": "BM101", "credits": 5},
    ]

    courses = []
    for course_data in courses_data:
        course = Course.query.filter_by(title=course_data["title"]).first()
        if not course:
            # Aquí asignamos el código y los créditos al crear el curso
            course = Course(
                title=course_data["title"],
                code=course_data["code"],
                credits=course_data["credits"],
            )
            kanvas_db.session.add(course)
        else:
            print(f"\tEl curso '{course_data['title']}' ya existe, no se añadirá de nuevo.")

        courses.append(course)

    kanvas_db.session.commit()

    if len(courses) < len(courses_data):
        print("Error: No se pudieron obtener todos los cursos correctamente.\n")
    else:
        print("Cursos creados correctamente!\n")

    print("Creando instancias de cursos...")
    for course in courses:
        for _ in range(random.randint(1, 5)):
            course_instance = CourseInstance(
                course_id=course.id,
                year=random.randint(2015, 2025),
                semester=random.choice([Semester.FIRST, Semester.SECOND]),
            )
            kanvas_db.session.add(course_instance)

    kanvas_db.session.commit()
    print("Instancias de cursos creadas correctamente!\n")

    print("Creando secciones...")
    course_instances = CourseInstance.query.all()
    for instance in course_instances:
        for _ in range(random.randint(1, 3)):
            unique_code = False
            while not unique_code:
                code = random.randint(100, 999)
                if not Section.query.filter_by(code=code).first():
                    unique_code = True
            teacher = random.choice(Teacher.query.all())
            section = Section(
                course_instance_id=instance.id,
                code=code,
                weighing_type=random.choice([WeighingType.PERCENTAGE, WeighingType.WEIGHT]),
                teacher=teacher,
            )
            kanvas_db.session.add(section)

    kanvas_db.session.commit()
    print("Secciones creadas correctamente!\n")

    print("Creando requisitos...")
    for course in courses:
        possible_prerequisites = [c for c in courses if c.id != course.id]
        num_prerequisites = random.randint(1, min(3, len(possible_prerequisites)))

        selected_prerequisites = random.sample(possible_prerequisites, num_prerequisites)
        for prerequisite in selected_prerequisites:
            if not Requisite.query.filter_by(
                course_id=course.id, course_requisite_id=prerequisite.id
            ).first():
                requisite = Requisite(course_id=course.id, course_requisite_id=prerequisite.id)
                kanvas_db.session.add(requisite)
    kanvas_db.session.commit()
    print("Requisitos creados correctamente!\n")

    print("Datos creados correctamente!")


if __name__ == "__main__":
    with kanvas_app.app_context():
        seed_database()

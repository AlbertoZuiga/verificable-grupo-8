import json
import re
from collections import defaultdict
from datetime import datetime

from app.models import (Classroom, Course, CourseInstance, Evaluation,
                        EvaluationInstance, Section, Semester, Student,
                        StudentSection, Teacher, User, WeighingType)
from app.utils import json_constants as JC


def parse_classroom_json(json_data):
    classrooms = []
    data = json.loads(json_data)

    if JC.CLASSROOMS not in data:
        raise ValueError(f"Falta la clave '{JC.CLASSROOMS}' en el JSON.")

    json_dictionary = data[JC.CLASSROOMS]
    ids_seen = set()

    for item in json_dictionary:
        for key in (JC.ID, JC.NAME, JC.CAPACITY):
            if key not in item:
                raise ValueError(
                    f"Falta la clave '{key}'\
                     en un elemento de "
                    f"'{JC.CLASSROOMS}'."
                )

        if not isinstance(item[JC.ID], int):
            raise ValueError(
                f"El campo '{JC.ID}' debe ser un número entero en un "
                f"elemento de '{JC.CLASSROOMS}'."
            )
        if not isinstance(item[JC.NAME], str):
            raise ValueError(
                f"El campo '{JC.NAME}' debe ser una cadena de texto en un "
                f"elemento de '{JC.CLASSROOMS}'."
            )
        if not isinstance(item[JC.CAPACITY], int):
            raise ValueError(
                f"El campo '{JC.CAPACITY}' debe ser un número entero en un "
                f"elemento de '{JC.CLASSROOMS}'."
            )

        name = item[JC.NAME]
        if len(name) == 0 or len(name) > 60:
            raise ValueError(
                "El largo del nombre debe ser mayor que 0 y menor o igual que 60 caracteres."
            )

        capacity = item[JC.CAPACITY]
        if capacity < 0 or capacity > 1000:
            raise ValueError("La capacidad debe ser mayor o igual a 0 y menor o igual que 1000.")

        if item[JC.ID] in ids_seen:
            raise ValueError(f"ID duplicado '{item[JC.ID]}' encontrado en " f"'{JC.CLASSROOMS}'.")
        ids_seen.add(item[JC.ID])

        classroom = Classroom(
            id=item[JC.ID],
            name=item[JC.NAME],
            capacity=item[JC.CAPACITY],
        )
        classrooms.append(classroom)

    return classrooms


def parse_students_json(json_data):
    result = []
    data = json.loads(json_data)

    if JC.STUDENTS not in data:
        raise ValueError(f"Falta la clave '{JC.STUDENTS}' en el JSON.")

    student_list = data[JC.STUDENTS]
    ids_seen = set()
    emails_seen = set()
    current_year = datetime.now().year

    for item in student_list:
        # Verificar claves requeridas
        for key in (JC.NAME, JC.EMAIL, JC.ID, JC.ENTRY_YEAR):
            if key not in item:
                raise ValueError(
                    f"Falta la clave '{key}'\
                     en un elemento de '{JC.STUDENTS}'."
                )

        # Verificar tipos de datos
        if not isinstance(item[JC.NAME], str):
            raise ValueError(
                f"El campo '{JC.NAME}' debe ser una cadena de texto en un "
                f"elemento de '{JC.STUDENTS}'."
            )
        if not isinstance(item[JC.EMAIL], str):
            raise ValueError(
                f"El campo '{JC.EMAIL}' debe ser una cadena de texto en un "
                f"elemento de '{JC.STUDENTS}'."
            )
        if not isinstance(item[JC.ID], int):
            raise ValueError(
                f"El campo '{JC.ID}' debe ser un número entero en un "
                f"elemento de '{JC.STUDENTS}'."
            )
        if not isinstance(item[JC.ENTRY_YEAR], int):
            raise ValueError(
                f"El campo '{JC.ENTRY_YEAR}' debe ser un número entero en un "
                f"elemento de '{JC.STUDENTS}'."
            )

        entry_year = item[JC.ENTRY_YEAR]
        if not current_year - 20 <= entry_year <= current_year + 5:
            raise ValueError(
                f"El campo '{JC.ENTRY_YEAR}' debe estar entre "
                f"{current_year - 20} y {current_year + 5}\
                     en un elemento de "
                f"'{JC.STUDENTS}'."
            )

        student_id = item[JC.ID]
        email = item[JC.EMAIL]
        name = item[JC.NAME]

        if student_id in ids_seen:
            raise ValueError(f"ID duplicado '{student_id}' encontrado en '{JC.STUDENTS}'.")
        if email in emails_seen:
            raise ValueError(f"Email duplicado '{email}' encontrado en '{JC.STUDENTS}'.")

        ids_seen.add(student_id)
        emails_seen.add(email)

        # Verificar unicidad en la base de datos
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            raise ValueError(f"Ya existe un usuario con el correo '{email}'.")

        existing_student = Student.query.filter_by(id=student_id).first()
        if existing_student:
            raise ValueError(f"Ya existe un estudiante con ID '{student_id}'.")

        # Validación de contenido
        if len(name) == 0 or len(name) > 60:
            raise ValueError(
                "El largo del nombre debe ser mayor que 0 y menor o igual que 60 caracteres."
            )
        if len(email) == 0 or len(email) > 60:
            raise ValueError(
                "El largo del correo debe ser mayor que 0 y menor o igual que 60 caracteres."
            )

        email_regex = r"^[\w\.-]+@[\w\.-]+\.\w+$"
        if not re.match(email_regex, email):
            raise ValueError(f"El correo '{email}' no tiene un formato válido.")

        name_parts = name.split()
        first_name = name_parts[0]
        last_name = " ".join(name_parts[1:]) if len(name_parts) > 1 else ""

        user = User(first_name=first_name, last_name=last_name, email=email)
        user.set_password(f"password_{first_name}")

        student = Student(id=student_id, user=user, university_entry_year=entry_year)

        result.append((user, student))

    return result


def parse_teachers_json(json_data):
    result = []
    data = json.loads(json_data)

    if JC.TEACHERS not in data:
        raise ValueError(f"Falta la clave '{JC.TEACHERS}' en el JSON.")

    teacher_list = data[JC.TEACHERS]
    ids_seen = set()
    emails_seen = set()

    for item in teacher_list:
        for key in (JC.NAME, JC.EMAIL, JC.ID):
            if key not in item:
                raise ValueError(
                    f"Falta la clave '{key}'\
                     en un elemento de '{JC.TEACHERS}'."
                )

        if not isinstance(item[JC.NAME], str):
            raise ValueError(
                f"El campo '{JC.NAME}' debe ser una cadena de texto en un "
                f"elemento de '{JC.TEACHERS}'."
            )
        if not isinstance(item[JC.EMAIL], str):
            raise ValueError(
                f"El campo '{JC.EMAIL}' debe ser una cadena de texto en un "
                f"elemento de '{JC.TEACHERS}'."
            )
        if not isinstance(item[JC.ID], int):
            raise ValueError(
                f"El campo '{JC.ID}' debe ser un número entero en un "
                f"elemento de '{JC.TEACHERS}'."
            )

        name = item[JC.NAME]
        email = item[JC.EMAIL]
        teacher_id = item[JC.ID]

        if len(name) == 0 or len(name) > 60:
            raise ValueError(
                "El largo del nombre debe ser mayor que 0 y menor o igual que 60 caracteres."
            )

        if len(email) == 0 or len(email) > 60:
            raise ValueError(
                "El largo del correo debe ser mayor que 0 y menor o igual que 60 caracteres."
            )

        email_regex = r"^[\w\.-]+@[\w\.-]+\.\w+$"
        if not re.match(email_regex, email):
            raise ValueError(f"El correo '{email}' no tiene un formato válido.")

        if teacher_id in ids_seen:
            raise ValueError(f"ID duplicado '{teacher_id}' encontrado en '{JC.TEACHERS}'.")
        if email in emails_seen:
            raise ValueError(f"Email duplicado '{email}' encontrado en '{JC.TEACHERS}'.")
        ids_seen.add(teacher_id)
        emails_seen.add(email)

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            raise ValueError(f"Ya existe un usuario con el correo '{email}'.")

        existing_teacher = Teacher.query.filter_by(id=teacher_id).first()
        if existing_teacher:
            raise ValueError(f"Ya existe un profesor con ID '{teacher_id}'.")

        name_parts = name.split()
        first_name = name_parts[0]
        last_name = " ".join(name_parts[1:]) if len(name_parts) > 1 else ""

        user = User(first_name=first_name, last_name=last_name, email=email)
        user.set_password(f"password_{name}")

        teacher = Teacher(id=teacher_id, user=user)

        result.append((user, teacher))

    return result


def parse_courses_json(json_data):
    data = json.loads(json_data)

    if JC.COURSES not in data:
        raise ValueError(f"Falta la clave '{JC.COURSES}' en el JSON.")

    course_list = data[JC.COURSES]
    courses = []
    requisite_code_pairs = []

    ids_seen = set()
    codes_seen = set()

    for item in course_list:
        # Validar existencia de claves
        for key in (JC.ID, JC.CODE, JC.DESCRIPTION, JC.CREDITS):
            if key not in item:
                raise ValueError(
                    f"Falta la clave '{key}'\
                    en un elemento de '{JC.COURSES}'."
                )

        # Validar tipos de datos
        if not isinstance(item[JC.ID], int):
            raise ValueError(
                f"El campo '{JC.ID}' debe ser un número entero\
                     en un elemento de '{JC.COURSES}'."
            )
        if not isinstance(item[JC.CODE], str):
            raise ValueError(
                f"El campo '{JC.CODE}' debe ser una cadena de texto\
                     en un elemento de '{JC.COURSES}'."
            )
        if not isinstance(item[JC.DESCRIPTION], str):
            raise ValueError(
                f"El campo '{JC.DESCRIPTION}' debe ser una cadena de texto\
                     en un elemento de '{JC.COURSES}'."
            )
        if not isinstance(item[JC.CREDITS], int):
            raise ValueError(
                f"El campo '{JC.CREDITS}' debe ser un número entero\
                     en un elemento de '{JC.COURSES}'."
            )

        # Validar unicidad
        course_id = item[JC.ID]
        course_code = item[JC.CODE]

        if course_id in ids_seen:
            raise ValueError(f"ID duplicado '{course_id}' encontrado en '{JC.COURSES}'.")
        if course_code in codes_seen:
            raise ValueError(f"Código duplicado '{course_code}' encontrado en '{JC.COURSES}'.")
        ids_seen.add(course_id)
        codes_seen.add(course_code)

        # Validar requisitos
        if JC.REQUISITES in item and not isinstance(item[JC.REQUISITES], list):
            raise ValueError(
                f"El campo '{JC.REQUISITES}' debe ser una lista\
                     en un elemento de '{JC.COURSES}'."
            )

        # Validar contenido
        if len(course_code) == 0 or len(course_code) > 15:
            raise ValueError(
                f"El campo '{JC.CODE}' debe ser más largo que 0 y más corto que 15 caracteres."
            )
        if len(item[JC.DESCRIPTION]) == 0 or len(item[JC.DESCRIPTION]) > 60:
            raise ValueError(
                f"El campo '{JC.DESCRIPTION}' debe ser\
                    más largo que 0 y más corto que 60 caracteres."
            )
        if not 0 < item[JC.CREDITS] <= 15:
            raise ValueError(
                f"El campo '{JC.CREDITS}' debe ser mayor que 0 y menor o igual que 15."
            )

        # Agregar curso
        course = Course(
            id=course_id,
            code=course_code,
            title=item[JC.DESCRIPTION],
            credits=item[JC.CREDITS],
        )
        courses.append(course)

        # Agregar relaciones de requisitos
        for req_code in item.get(JC.REQUISITES, []):
            requisite_code_pairs.append((course_code, req_code))

    def detect_cycle(graph):
        visited = set()
        recursion_stack = set()

        def dfs(node):
            visited.add(node)
            recursion_stack.add(node)
            for neighbor in graph[node]:
                if neighbor not in visited:
                    if dfs(neighbor):
                        return True
                elif neighbor in recursion_stack:
                    return True
            recursion_stack.remove(node)
            return False

        for node in list(graph):
            if node not in visited:
                if dfs(node):
                    return True
        return False

    # Verificar ciclos en los requisitos
    graph = defaultdict(list)
    for course_code, req_code in requisite_code_pairs:
        graph[course_code].append(req_code)

    if detect_cycle(graph):
        raise ValueError("Se detectó un ciclo en los requisitos de los cursos.")

    return courses, requisite_code_pairs


def parse_course_instances_json(json_data):
    data = json.loads(json_data)
    valid_course_ids = {course.id for course in Course.query.all()}

    if JC.YEAR not in data:
        raise ValueError(f"Falta la clave '{JC.YEAR}' en el JSON.")
    if JC.SEMESTER not in data:
        raise ValueError(f"Falta la clave '{JC.SEMESTER}' en el JSON.")
    if JC.COURSE_INSTANCES not in data:
        raise ValueError(f"Falta la clave '{JC.COURSE_INSTANCES}' en el JSON.")

    year = data[JC.YEAR]
    semester_value = data[JC.SEMESTER]
    course_instances_list = data[JC.COURSE_INSTANCES]
    current_year = datetime.now().year

    # Validación de año
    if not isinstance(year, int):
        raise ValueError(f"El campo '{JC.YEAR}' debe ser un número entero.")
    if not current_year - 5 <= year <= current_year + 5:
        raise ValueError(
            f"El campo '{JC.YEAR}' debe estar entre " f"{current_year - 5} y {current_year + 5}."
        )

    # Validación de semestre
    try:
        semester_enum = Semester(semester_value)
    except ValueError as error:
        valid_values = [s.value for s in Semester]
        raise ValueError(
            f"Valor de semestre inválido '{semester_value}'. "
            f"Los valores permitidos son: {valid_values}."
        ) from error

    instances = []
    seen_ids = set()
    seen_course_ids = set()

    for index, item in enumerate(course_instances_list):
        # Validar claves requeridas
        if JC.ID not in item:
            raise ValueError(
                f"Falta la clave '{JC.ID}'\
                    en el elemento {index} de '{JC.COURSE_INSTANCES}'."
            )
        if JC.COURSE_ID not in item:
            raise ValueError(
                f"Falta la clave '{JC.COURSE_ID}'\
                    en el elemento {index} de '{JC.COURSE_INSTANCES}'."
            )

        instance_id = item[JC.ID]
        course_id = item[JC.COURSE_ID]

        # Validar tipos de datos
        if not isinstance(instance_id, int):
            raise ValueError(
                f"El campo '{JC.ID}' debe ser un número entero en el elemento {index}."
            )
        if not isinstance(course_id, int):
            raise ValueError(
                f"El campo '{JC.COURSE_ID}' debe ser un número entero en el elemento {index}."
            )

        # Validar existencia de course_id
        if course_id not in valid_course_ids:
            raise ValueError(f"El 'course_id' {course_id} no existe en la lista de cursos válidos.")

        # Validar unicidad
        if instance_id in seen_ids:
            raise ValueError(f"ID duplicado encontrado: {instance_id} en el elemento {index}.")
        if course_id in seen_course_ids:
            raise ValueError(
                f"'course_id' duplicado encontrado: {course_id} en el elemento {index}."
            )

        seen_ids.add(instance_id)
        seen_course_ids.add(course_id)

        instance = CourseInstance(
            id=instance_id, course_id=course_id, year=year, semester=semester_enum
        )
        instances.append(instance)

    return instances


def parse_sections_json(json_data):
    data = json.loads(json_data)

    parsed_sections = []
    parsed_evaluations = []
    parsed_instances = []

    if JC.SECTIONS not in data:
        raise ValueError(f"Falta la clave '{JC.SECTIONS}' en el JSON.")

    for section_data in data[JC.SECTIONS]:
        # Validación de claves en sección
        required_section_keys = [
            JC.EVALUATION,
            JC.ID,
            JC.COURSE_INSTANCE,
            JC.TEACHER_ID,
        ]
        for key in required_section_keys:
            if key not in section_data:
                raise ValueError(
                    f"Falta la clave '{key}'\
                     en un elemento de '{JC.SECTIONS}'."
                )

        evaluation_data = section_data[JC.EVALUATION]

        # Validación de claves en evaluación
        required_eval_keys = [JC.EVALUATION_TYPE, JC.TOPIC_COMBINATIONS, JC.TOPICS]
        for key in required_eval_keys:
            if key not in evaluation_data:
                raise ValueError(
                    f"Falta la clave '{key}' en la evaluación de un "
                    f"elemento de '{JC.SECTIONS}'."
                )

        # Validación de tipos básicos
        if not isinstance(section_data[JC.ID], int):
            raise ValueError(
                f"El campo '{JC.ID}' debe ser un número entero en un "
                f"elemento de '{JC.SECTIONS}'."
            )
        if not isinstance(section_data[JC.COURSE_INSTANCE], int):
            raise ValueError(
                f"El campo '{JC.COURSE_INSTANCE}' debe ser un número entero "
                f"en un elemento de '{JC.SECTIONS}'."
            )
        if not isinstance(section_data[JC.TEACHER_ID], int):
            raise ValueError(
                f"El campo '{JC.TEACHER_ID}' debe ser un número entero en un "
                f"elemento de '{JC.SECTIONS}'."
            )

        # Validación de profesor
        teacher_id = section_data[JC.TEACHER_ID]
        if not Teacher.query.filter_by(id=teacher_id).first():
            raise ValueError(f"No existe un profesor con ID '{teacher_id}'.")

        # Validación de tipos en evaluación
        eval_type_raw = evaluation_data[JC.EVALUATION_TYPE]
        if not isinstance(eval_type_raw, str):
            raise ValueError(
                f"El campo '{JC.EVALUATION_TYPE}' debe ser una cadena de texto "
                f"en la evaluación de un elemento de '{JC.SECTIONS}'."
            )
        if not isinstance(evaluation_data[JC.TOPIC_COMBINATIONS], list):
            raise ValueError(
                f"El campo '{JC.TOPIC_COMBINATIONS}' debe ser una lista "
                f"en la evaluación de un elemento de '{JC.SECTIONS}'."
            )
        if not isinstance(evaluation_data[JC.TOPICS], dict):
            raise ValueError(
                f"El campo '{JC.TOPICS}' debe ser un diccionario "
                f"en la evaluación de un elemento de '{JC.SECTIONS}'."
            )

        normalized_type = eval_type_raw.strip().capitalize()
        try:
            weighing_type = WeighingType(normalized_type)
        except ValueError as err:
            valid_types = [w.value for w in WeighingType]
            raise ValueError(
                f"Tipo de evaluación inválido: '{eval_type_raw}'. "
                f"Los tipos permitidos son: {valid_types}."
            ) from err

        topic_combinations = evaluation_data[JC.TOPIC_COMBINATIONS]
        topic_details = evaluation_data[JC.TOPICS]

        # Crear sección
        section = Section(
            id=section_data[JC.ID],
            code=section_data[JC.ID],
            course_instance_id=section_data[JC.COURSE_INSTANCE],
            teacher_id=teacher_id,
            weighing_type=weighing_type,
        )
        parsed_sections.append(section)

        # Normalizar ponderaciones
        if weighing_type == WeighingType.PERCENTAGE:
            total = sum(topic[JC.TOPIC_WEIGHT] for topic in topic_combinations)
            if total not in (0, 100):
                for topic in topic_combinations:
                    original = topic[JC.TOPIC_WEIGHT]
                    topic[JC.TOPIC_WEIGHT] = round((original / total) * 100, 2)

        # Procesar evaluaciones
        for topic in topic_combinations:
            if JC.ID not in topic:
                raise ValueError(
                    f"Falta la clave '{JC.ID}' en un topic de " f"'{JC.TOPIC_COMBINATIONS}'."
                )

            topic_id = topic[JC.ID]
            topic_name = topic[JC.NAME]
            if str(topic_id) not in topic_details:
                raise ValueError(
                    f"Falta la definición para el topic id '{topic_id}' " f"en '{JC.TOPICS}'."
                )

            topic_def = topic_details[str(topic_id)]

            for key in [
                JC.EVALUATION_TYPE,
                JC.TOPIC_VALUES,
                JC.TOPIC_COUNT,
                JC.TOPIC_MANDATORY,
            ]:
                if key not in topic_def:
                    raise ValueError(
                        f"Falta la clave '{key}' en la definición de " f"topic '{topic_id}'."
                    )

            raw_eval_type = topic_def[JC.EVALUATION_TYPE]
            if not isinstance(raw_eval_type, str):
                raise ValueError(
                    f"El campo '{JC.EVALUATION_TYPE}' debe ser una cadena de texto "
                    f"en la definición de topic '{topic_id}'."
                )
            if not isinstance(topic_def[JC.TOPIC_VALUES], list):
                raise ValueError(
                    f"El campo '{JC.TOPIC_VALUES}' debe ser una lista en "
                    f"la definición de topic '{topic_id}'."
                )
            if not isinstance(topic_def[JC.TOPIC_MANDATORY], list):
                raise ValueError(
                    f"El campo '{JC.TOPIC_MANDATORY}' debe ser una lista en "
                    f"la definición de topic '{topic_id}'."
                )
            if not isinstance(topic_def[JC.TOPIC_COUNT], int):
                raise ValueError(
                    f"El campo '{JC.TOPIC_COUNT}' debe ser un número entero en "
                    f"la definición de topic '{topic_id}'."
                )

            count = topic_def[JC.TOPIC_COUNT]
            if len(topic_def[JC.TOPIC_VALUES]) != count:
                raise ValueError(
                    f"El tamaño de '{JC.TOPIC_VALUES}' no coincide con "
                    f"'{JC.TOPIC_COUNT}' en la definición de topic '{topic_id}'."
                )
            if len(topic_def[JC.TOPIC_MANDATORY]) != count:
                raise ValueError(
                    f"El tamaño de '{JC.TOPIC_MANDATORY}' no coincide con "
                    f"'{JC.TOPIC_COUNT}' en la definición de topic '{topic_id}'."
                )

            normalized_eval_type = raw_eval_type.strip().capitalize()
            try:
                topic_weighing_type = WeighingType(normalized_eval_type)
            except ValueError as err:
                valid_types = [w.value for w in WeighingType]
                raise ValueError(
                    f"Tipo de evaluación inválido: '{raw_eval_type}'. "
                    f"Los tipos permitidos son: {valid_types}."
                ) from err

            if topic_weighing_type == WeighingType.PERCENTAGE:
                total = sum(topic_def[JC.TOPIC_VALUES])
                if total not in (0, 100):
                    topic_def[JC.TOPIC_VALUES] = [
                        round((v / total) * 100, 2) for v in topic_def[JC.TOPIC_VALUES]
                    ]
                if round(sum(topic_def[JC.TOPIC_VALUES]), 2) != 100:
                    raise ValueError(
                        f"La suma de ponderaciones en '{JC.TOPIC_VALUES}' "
                        f"debe ser 100 en la definición de topic '{topic_id}'."
                    )

            evaluation = Evaluation(
                id=topic_id,
                section=section,
                title=topic_name,
                weighing=topic[JC.TOPIC_WEIGHT],
                weighing_system=topic_weighing_type,
            )
            parsed_evaluations.append(evaluation)

            for i in range(count):
                instance = EvaluationInstance(
                    evaluation=evaluation,
                    index_in_evaluation=i + 1,
                    title=f"{topic_name} {i + 1}",
                    instance_weighing=topic_def[JC.TOPIC_VALUES][i],
                    optional=topic_def[JC.TOPIC_MANDATORY][i],
                )
                parsed_instances.append(instance)

    print(
        f"[DEBUG] Parsed {len(parsed_sections)} sections, "
        f"{len(parsed_evaluations)} evaluations, and "
        f"{len(parsed_instances)} evaluation instances."
    )
    return parsed_sections, parsed_evaluations, parsed_instances


def parse_student_sections_json(json_data):
    data = json.loads(json_data)

    if JC.STUDENT_SECTIONS not in data:
        raise ValueError(f"Falta la clave '{JC.STUDENT_SECTIONS}' en el JSON.")

    student_section_data = data[JC.STUDENT_SECTIONS]
    parsed_links = []
    visited_links = set()

    for item in student_section_data:
        if JC.SECTION_ID not in item:
            raise ValueError(
                f"Falta la clave '{JC.SECTION_ID}'\
                     en un elemento de "
                f"'{JC.STUDENT_SECTIONS}'."
            )

        if JC.STUDENT_ID not in item:
            raise ValueError(
                f"Falta la clave '{JC.STUDENT_ID}'\
                     en un elemento de "
                f"'{JC.STUDENT_SECTIONS}'."
            )

        section_id = item[JC.SECTION_ID]
        student_id = item[JC.STUDENT_ID]

        if not isinstance(section_id, int):
            raise ValueError(
                f"El campo '{JC.SECTION_ID}' debe ser un número entero en un "
                f"elemento de '{JC.STUDENT_SECTIONS}'."
            )

        if not isinstance(student_id, int):
            raise ValueError(
                f"El campo '{JC.STUDENT_ID}' debe ser un número entero en un "
                f"elemento de '{JC.STUDENT_SECTIONS}'."
            )

        link = (section_id, student_id)
        if link in visited_links:
            raise ValueError(
                f"Relación entre estudiante '{student_id}' y sección " f"'{section_id}' repetida."
            )
        visited_links.add(link)

        if not Section.query.filter_by(id=section_id).first():
            raise ValueError(f"No existe una sección con ID '{section_id}'.")

        if not Student.query.filter_by(id=student_id).first():
            raise ValueError(f"No existe un estudiante con ID '{student_id}'.")

        if StudentSection.query.filter_by(section_id=section_id, student_id=student_id).first():
            raise ValueError(
                f"La relación entre estudiante '{student_id}' y sección "
                f"'{section_id}' ya existe."
            )

        parsed_links.append(StudentSection(section_id=section_id, student_id=student_id))

    return parsed_links


def parse_grades_json(json_data):
    data = json.loads(json_data)

    if JC.GRADES not in data:
        raise ValueError(f"Falta la clave '{JC.GRADES}' en el JSON.")

    grades_raw = data[JC.GRADES]
    parsed_grades = []
    visited_grades = set()

    for entry in grades_raw:
        if JC.STUDENT_ID not in entry:
            raise ValueError(
                f"Falta la clave '{JC.STUDENT_ID}'\
                 en un elemento de '{JC.GRADES}'."
            )
        if JC.TOPIC_ID not in entry:
            raise ValueError(
                f"Falta la clave '{JC.TOPIC_ID}'\
                 en un elemento de '{JC.GRADES}'."
            )
        if JC.INSTANCE not in entry:
            raise ValueError(
                f"Falta la clave '{JC.INSTANCE}'\
                 en un elemento de '{JC.GRADES}'."
            )
        if JC.GRADE not in entry:
            raise ValueError(
                f"Falta la clave '{JC.GRADE}'\
                 en un elemento de '{JC.GRADES}'."
            )

        student_id = entry[JC.STUDENT_ID]
        topic_id = entry[JC.TOPIC_ID]
        instance_index = entry[JC.INSTANCE]
        grade_value = entry[JC.GRADE]

        if not isinstance(student_id, int):
            raise ValueError(
                f"El campo '{JC.STUDENT_ID}' debe ser un número entero\
                     en un elemento de '{JC.GRADES}'."
            )
        if not isinstance(topic_id, int):
            raise ValueError(
                f"El campo '{JC.TOPIC_ID}' debe ser un número entero\
                     en un elemento de '{JC.GRADES}'."
            )
        if not isinstance(instance_index, int):
            raise ValueError(
                f"El campo '{JC.INSTANCE}' debe ser un número entero\
                     en un elemento de '{JC.GRADES}'."
            )
        if not isinstance(grade_value, (int, float)):
            raise ValueError(
                f"El campo '{JC.GRADE}' debe ser un número\
                     en un elemento de '{JC.GRADES}'."
            )
        if not 1 <= grade_value <= 7:
            raise ValueError(
                f"La nota '{grade_value}' no es válida. Debe ser un número entre 1 y 7."
            )

        student = Student.query.filter_by(id=student_id).first()
        if not student:
            raise ValueError(f"No existe un estudiante con ID '{student_id}'.")

        evaluation_instance = EvaluationInstance.query.filter_by(
            evaluation_id=topic_id, index_in_evaluation=instance_index
        ).first()
        if not evaluation_instance:
            raise ValueError(
                f"No existe una instancia de evaluación con evaluación ID "
                f"'{topic_id}' e índice {instance_index}."
            )

        if evaluation_instance.evaluation.section not in student.sections:
            raise ValueError(
                f"Evaluación {evaluation_instance.title} no es parte de las "
                f"secciones del alumno {student.user.first_name} {student.user.last_name}."
            )

        grade_key = (student_id, topic_id, instance_index)
        if grade_key in visited_grades:
            raise ValueError(
                f"Combinación (student_id, topic_id, instance_index)={grade_key} "
                f"se encuentra duplicada."
            )
        visited_grades.add(grade_key)

        parsed_grades.append(
            {
                "student_id": student_id,
                "topic_id": topic_id,
                "instance_index": instance_index,
                "grade": grade_value,
            }
        )

    return parsed_grades

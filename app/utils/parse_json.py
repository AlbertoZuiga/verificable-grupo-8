import json
import re
from collections import defaultdict
from datetime import datetime

from app.models import (
    Classroom,
    Course,
    CourseInstance,
    Evaluation,
    EvaluationInstance,
    Section,
    Semester,
    Student,
    StudentSection,
    Teacher,
    User,
    WeighingType,
)
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
        _validate_required_keys(item)
        _validate_field_types(item, current_year)
        _check_uniqueness(item, ids_seen, emails_seen)
        _check_db_duplicates(item)

        user, student = _create_user_and_student(item)
        result.append((user, student))

    return result


def _validate_required_keys(item):
    for key in (JC.NAME, JC.EMAIL, JC.ID, JC.ENTRY_YEAR):
        if key not in item:
            raise ValueError(f"Falta la clave '{key}' en un elemento de '{JC.STUDENTS}'.")


def _validate_field_types(item, current_year):
    if not isinstance(item[JC.NAME], str):
        raise ValueError(f"El campo '{JC.NAME}' debe ser una cadena de texto.")
    if not isinstance(item[JC.EMAIL], str):
        raise ValueError(f"El campo '{JC.EMAIL}' debe ser una cadena de texto.")
    if not isinstance(item[JC.ID], int):
        raise ValueError(f"El campo '{JC.ID}' debe ser un número entero.")
    if not isinstance(item[JC.ENTRY_YEAR], int):
        raise ValueError(f"El campo '{JC.ENTRY_YEAR}' debe ser un número entero.")

    entry_year = item[JC.ENTRY_YEAR]
    if not current_year - 20 <= entry_year <= current_year + 5:
        raise ValueError(
            f"El campo '{JC.ENTRY_YEAR}' debe estar entre {current_year - 20} y {current_year + 5}."
        )

    name = item[JC.NAME]
    email = item[JC.EMAIL]

    if not 0 < len(name) <= 60:
        raise ValueError(
            "El largo del nombre debe ser mayor que 0 y menor o igual que 60 caracteres."
        )
    if not 0 < len(email) <= 60:
        raise ValueError(
            "El largo del correo debe ser mayor que 0 y menor o igual que 60 caracteres."
        )

    email_regex = r"^[\w\.-]+@[\w\.-]+\.\w+$"
    if not re.match(email_regex, email):
        raise ValueError(f"El correo '{email}' no tiene un formato válido.")


def _check_uniqueness(item, ids_seen, emails_seen):
    student_id = item[JC.ID]
    email = item[JC.EMAIL]

    if student_id in ids_seen:
        raise ValueError(f"ID duplicado '{student_id}' encontrado.")
    if email in emails_seen:
        raise ValueError(f"Email duplicado '{email}' encontrado.")

    ids_seen.add(student_id)
    emails_seen.add(email)


def _check_db_duplicates(item):
    student_id = item[JC.ID]
    email = item[JC.EMAIL]

    if User.query.filter_by(email=email).first():
        raise ValueError(f"Ya existe un usuario con el correo '{email}'.")
    if Student.query.filter_by(id=student_id).first():
        raise ValueError(f"Ya existe un estudiante con ID '{student_id}'.")


def _create_user_and_student(item):
    name_parts = item[JC.NAME].split()
    first_name = name_parts[0]
    last_name = " ".join(name_parts[1:]) if len(name_parts) > 1 else ""

    email = item[JC.EMAIL]
    student_id = item[JC.ID]
    entry_year = item[JC.ENTRY_YEAR]

    user = User(first_name=first_name, last_name=last_name, email=email)
    user.set_password(f"password_{first_name}")

    student = Student(id=student_id, user=user, university_entry_year=entry_year)
    return user, student


def parse_teachers_json(json_data):
    result = []
    data = json.loads(json_data)

    if JC.TEACHERS not in data:
        raise ValueError(f"Falta la clave '{JC.TEACHERS}' en el JSON.")

    teacher_list = data[JC.TEACHERS]
    ids_seen = set()
    emails_seen = set()

    for item in teacher_list:
        _validate_teacher_keys(item)
        _validate_teacher_field_types(item)
        _validate_teacher_field_content(item)
        _check_teacher_uniqueness(item, ids_seen, emails_seen)
        _check_teacher_db_duplicates(item)

        user, teacher = _create_user_and_teacher(item)
        result.append((user, teacher))

    return result


def _validate_teacher_keys(item):
    for key in (JC.NAME, JC.EMAIL, JC.ID):
        if key not in item:
            raise ValueError(f"Falta la clave '{key}' en un elemento de '{JC.TEACHERS}'.")


def _validate_teacher_field_types(item):
    if not isinstance(item[JC.NAME], str):
        raise ValueError(f"El campo '{JC.NAME}' debe ser una cadena de texto.")
    if not isinstance(item[JC.EMAIL], str):
        raise ValueError(f"El campo '{JC.EMAIL}' debe ser una cadena de texto.")
    if not isinstance(item[JC.ID], int):
        raise ValueError(f"El campo '{JC.ID}' debe ser un número entero.")


def _validate_teacher_field_content(item):
    name = item[JC.NAME]
    email = item[JC.EMAIL]

    if not 0 < len(name) <= 60:
        raise ValueError(
            "El largo del nombre debe ser mayor que 0 y menor o igual que 60 caracteres."
        )
    if not 0 < len(email) <= 60:
        raise ValueError(
            "El largo del correo debe ser mayor que 0 y menor o igual que 60 caracteres."
        )

    email_regex = r"^[\w\.-]+@[\w\.-]+\.\w+$"
    if not re.match(email_regex, email):
        raise ValueError(f"El correo '{email}' no tiene un formato válido.")


def _check_teacher_uniqueness(item, ids_seen, emails_seen):
    teacher_id = item[JC.ID]
    email = item[JC.EMAIL]

    if teacher_id in ids_seen:
        raise ValueError(f"ID duplicado '{teacher_id}' encontrado en '{JC.TEACHERS}'.")
    if email in emails_seen:
        raise ValueError(f"Email duplicado '{email}' encontrado en '{JC.TEACHERS}'.")

    ids_seen.add(teacher_id)
    emails_seen.add(email)


def _check_teacher_db_duplicates(item):
    teacher_id = item[JC.ID]
    email = item[JC.EMAIL]

    if User.query.filter_by(email=email).first():
        raise ValueError(f"Ya existe un usuario con el correo '{email}'.")
    if Teacher.query.filter_by(id=teacher_id).first():
        raise ValueError(f"Ya existe un profesor con ID '{teacher_id}'.")


def _create_user_and_teacher(item):
    name_parts = item[JC.NAME].split()
    first_name = name_parts[0]
    last_name = " ".join(name_parts[1:]) if len(name_parts) > 1 else ""

    email = item[JC.EMAIL]
    teacher_id = item[JC.ID]

    user = User(first_name=first_name, last_name=last_name, email=email)
    user.set_password(f"password_{first_name}")

    teacher = Teacher(id=teacher_id, user=user)
    return user, teacher


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
        validate_course_keys(item)
        validate_course_types(item)
        validate_course_uniqueness(item, ids_seen, codes_seen)
        validate_course_constraints(item)

        course = build_course(item)
        courses.append(course)

        requisites = item.get(JC.REQUISITES, [])
        if requisites and not isinstance(requisites, list):
            raise ValueError(
                f"El campo '{JC.REQUISITES}' debe ser una lista en un elemento de '{JC.COURSES}'."
            )

        for req_code in requisites:
            requisite_code_pairs.append((item[JC.CODE], req_code))

    check_requisite_cycles(requisite_code_pairs)

    return courses, requisite_code_pairs


def validate_course_keys(item):
    for key in (JC.ID, JC.CODE, JC.DESCRIPTION, JC.CREDITS):
        if key not in item:
            raise ValueError(f"Falta la clave '{key}' en un elemento de '{JC.COURSES}'.")


def validate_course_types(item):
    if not isinstance(item[JC.ID], int):
        raise ValueError(f"'{JC.ID}' debe ser un entero en '{JC.COURSES}'.")
    if not isinstance(item[JC.CODE], str):
        raise ValueError(f"'{JC.CODE}' debe ser una cadena en '{JC.COURSES}'.")
    if not isinstance(item[JC.DESCRIPTION], str):
        raise ValueError(f"'{JC.DESCRIPTION}' debe ser una cadena en '{JC.COURSES}'.")
    if not isinstance(item[JC.CREDITS], int):
        raise ValueError(f"'{JC.CREDITS}' debe ser un entero en '{JC.COURSES}'.")


def validate_course_uniqueness(item, ids_seen, codes_seen):
    course_id = item[JC.ID]
    course_code = item[JC.CODE]

    if course_id in ids_seen:
        raise ValueError(f"ID duplicado '{course_id}' en '{JC.COURSES}'.")
    if course_code in codes_seen:
        raise ValueError(f"Código duplicado '{course_code}' en '{JC.COURSES}'.")

    ids_seen.add(course_id)
    codes_seen.add(course_code)


def validate_course_constraints(item):
    if not 0 < len(item[JC.CODE]) <= 15:
        raise ValueError(f"'{JC.CODE}' debe tener entre 1 y 15 caracteres.")
    if not 0 < len(item[JC.DESCRIPTION]) <= 60:
        raise ValueError(f"'{JC.DESCRIPTION}' debe tener entre 1 y 60 caracteres.")
    if not 0 < item[JC.CREDITS] <= 15:
        raise ValueError(f"'{JC.CREDITS}' debe estar entre 1 y 15.")


def build_course(item):
    return Course(
        id=item[JC.ID],
        code=item[JC.CODE],
        title=item[JC.DESCRIPTION],
        credits=item[JC.CREDITS],
    )


def check_requisite_cycles(requisite_pairs):
    graph = defaultdict(list)
    for course_code, req_code in requisite_pairs:
        graph[course_code].append(req_code)

    if detect_cycle(graph):
        raise ValueError("Se detectó un ciclo en los requisitos de los cursos.")


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

    return any(dfs(node) for node in graph if node not in visited)


def parse_course_instances_json(json_data):
    data = json.loads(json_data)
    valid_course_ids = {course.id for course in Course.query.all()}

    year = extract_and_validate_year(data)
    semester_enum = extract_and_validate_semester(data)
    course_instances_list = extract_and_validate_instances_list(data)

    instances = []
    seen_ids = set()
    seen_course_ids = set()

    for index, item in enumerate(course_instances_list):
        instance_id, course_id = extract_and_validate_instance_keys(item, index)
        validate_instance_types(instance_id, course_id, index)
        validate_course_id_exists(course_id, valid_course_ids)
        validate_instance_uniqueness(instance_id, course_id, seen_ids, seen_course_ids, index)

        instances.append(
            CourseInstance(
                id=instance_id,
                course_id=course_id,
                year=year,
                semester=semester_enum,
            )
        )

    return instances


def extract_and_validate_year(data):
    if JC.YEAR not in data:
        raise ValueError(f"Falta la clave '{JC.YEAR}' en el JSON.")

    year = data[JC.YEAR]
    current_year = datetime.now().year

    if not isinstance(year, int):
        raise ValueError(f"El campo '{JC.YEAR}' debe ser un número entero.")
    if not current_year - 5 <= year <= current_year + 5:
        raise ValueError(
            f"El campo '{JC.YEAR}' debe estar entre {current_year - 5} y {current_year + 5}."
        )

    return year


def extract_and_validate_semester(data):
    if JC.SEMESTER not in data:
        raise ValueError(f"Falta la clave '{JC.SEMESTER}' en el JSON.")

    semester_value = data[JC.SEMESTER]

    try:
        return Semester(semester_value)
    except ValueError as error:
        valid_values = [s.value for s in Semester]
        raise ValueError(
            f"Valor de semestre inválido '{semester_value}'. "
            f"Los valores permitidos son: {valid_values}."
        ) from error


def extract_and_validate_instances_list(data):
    if JC.COURSE_INSTANCES not in data:
        raise ValueError(f"Falta la clave '{JC.COURSE_INSTANCES}' en el JSON.")
    return data[JC.COURSE_INSTANCES]


def extract_and_validate_instance_keys(item, index):
    if JC.ID not in item:
        raise ValueError(
            f"Falta la clave '{JC.ID}' en el elemento {index} de '{JC.COURSE_INSTANCES}'."
        )
    if JC.COURSE_ID not in item:
        raise ValueError(
            f"Falta la clave '{JC.COURSE_ID}' en el elemento {index} de '{JC.COURSE_INSTANCES}'."
        )

    return item[JC.ID], item[JC.COURSE_ID]


def validate_instance_types(instance_id, course_id, index):
    if not isinstance(instance_id, int):
        raise ValueError(f"El campo '{JC.ID}' debe ser un número entero en el elemento {index}.")
    if not isinstance(course_id, int):
        raise ValueError(
            f"El campo '{JC.COURSE_ID}' debe ser un número entero en el elemento {index}."
        )


def validate_course_id_exists(course_id, valid_course_ids):
    if course_id not in valid_course_ids:
        raise ValueError(f"El 'course_id' {course_id} no existe en la lista de cursos válidos.")


def validate_instance_uniqueness(instance_id, course_id, seen_ids, seen_course_ids, index):
    if instance_id in seen_ids:
        raise ValueError(f"ID duplicado encontrado: {instance_id} en el elemento {index}.")
    if course_id in seen_course_ids:
        raise ValueError(f"'course_id' duplicado encontrado: {course_id} en el elemento {index}.")

    seen_ids.add(instance_id)
    seen_course_ids.add(course_id)


def parse_sections_json(json_data):
    data = json.loads(json_data)

    if JC.SECTIONS not in data:
        raise ValueError(f"Falta la clave '{JC.SECTIONS}' en el JSON.")

    parsed_sections = []
    parsed_evaluations = []
    parsed_instances = []

    for section_data in data[JC.SECTIONS]:
        section = _parse_section_header(section_data)
        parsed_sections.append(section)

        evaluation_data = section_data[JC.EVALUATION]
        topic_combinations = evaluation_data[JC.TOPIC_COMBINATIONS]
        topic_details = evaluation_data[JC.TOPICS]
        weighing_type = section.weighing_type

        _normalize_section_weights(weighing_type, topic_combinations)

        for topic in topic_combinations:
            evaluation, instances = _parse_evaluation(topic, topic_details, section)
            parsed_evaluations.append(evaluation)
            parsed_instances.extend(instances)

    print(
        f"[DEBUG] Parsed {len(parsed_sections)} sections, "
        f"{len(parsed_evaluations)} evaluations, and "
        f"{len(parsed_instances)} evaluation instances."
    )
    return parsed_sections, parsed_evaluations, parsed_instances


def _parse_section_header(section_data):
    _require_keys(section_data, [JC.ID, JC.COURSE_INSTANCE, JC.TEACHER_ID, JC.EVALUATION])
    _validate_teacher_exists(section_data[JC.TEACHER_ID])
    _validate_types(section_data, {JC.ID: int, JC.COURSE_INSTANCE: int, JC.TEACHER_ID: int})

    evaluation_data = section_data[JC.EVALUATION]
    _require_keys(evaluation_data, [JC.EVALUATION_TYPE, JC.TOPIC_COMBINATIONS, JC.TOPICS])
    _validate_types(
        evaluation_data, {JC.EVALUATION_TYPE: str, JC.TOPIC_COMBINATIONS: list, JC.TOPICS: dict}
    )

    weighing_type = _parse_weighing_type(evaluation_data[JC.EVALUATION_TYPE])
    return Section(
        id=section_data[JC.ID],
        code=section_data[JC.ID],
        course_instance_id=section_data[JC.COURSE_INSTANCE],
        teacher_id=section_data[JC.TEACHER_ID],
        weighing_type=weighing_type,
    )


def _normalize_section_weights(weighing_type, topic_combinations):
    if weighing_type != WeighingType.PERCENTAGE:
        return
    total = sum(t[JC.TOPIC_WEIGHT] for t in topic_combinations)
    if total not in (0, 100):
        for t in topic_combinations:
            t[JC.TOPIC_WEIGHT] = round((t[JC.TOPIC_WEIGHT] / total) * 100, 2)


def _parse_evaluation(topic, topic_details, section):
    _require_keys(topic, [JC.ID, JC.NAME])
    topic_id = topic[JC.ID]
    topic_name = topic[JC.NAME]

    if str(topic_id) not in topic_details:
        raise ValueError(f"Falta la definición para el topic id '{topic_id}' en '{JC.TOPICS}'.")

    topic_def = topic_details[str(topic_id)]
    _require_keys(
        topic_def, [JC.EVALUATION_TYPE, JC.TOPIC_VALUES, JC.TOPIC_COUNT, JC.TOPIC_MANDATORY]
    )
    _validate_types(
        topic_def,
        {
            JC.EVALUATION_TYPE: str,
            JC.TOPIC_VALUES: list,
            JC.TOPIC_MANDATORY: list,
            JC.TOPIC_COUNT: int,
        },
    )

    count = topic_def[JC.TOPIC_COUNT]
    _validate_topic_value_lengths(topic_def, topic_id, count)

    topic_weighing_type = _parse_weighing_type(topic_def[JC.EVALUATION_TYPE])
    _normalize_topic_values(topic_weighing_type, topic_def, topic_id)

    evaluation = Evaluation(
        id=topic_id,
        section=section,
        title=topic_name,
        weighing=topic[JC.TOPIC_WEIGHT],
        weighing_system=topic_weighing_type,
    )

    instances = [
        EvaluationInstance(
            evaluation=evaluation,
            index_in_evaluation=i + 1,
            title=f"{topic_name} {i + 1}",
            instance_weighing=topic_def[JC.TOPIC_VALUES][i],
            optional=topic_def[JC.TOPIC_MANDATORY][i],
        )
        for i in range(count)
    ]

    return evaluation, instances


def _validate_teacher_exists(teacher_id):
    if not Teacher.query.filter_by(id=teacher_id).first():
        raise ValueError(f"No existe un profesor con ID '{teacher_id}'.")


def _require_keys(data, keys):
    for key in keys:
        if key not in data:
            raise ValueError(f"Falta la clave '{key}'.")


def _validate_types(data, expected_types):
    for key, t in expected_types.items():
        if not isinstance(data[key], t):
            raise ValueError(f"El campo '{key}' debe ser del tipo {t.__name__}.")


def _validate_topic_value_lengths(topic_def, topic_id, count):
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


def _parse_weighing_type(value):
    try:
        return WeighingType(value.strip().capitalize())
    except ValueError as err:
        valid_types = [w.value for w in WeighingType]
        raise ValueError(
            f"Tipo de evaluación inválido: '{value}'. Los tipos permitidos son: {valid_types}."
        ) from err


def _normalize_topic_values(weighing_type, topic_def, topic_id):
    if weighing_type != WeighingType.PERCENTAGE:
        return

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
        _validate_grade_keys(entry)
        _validate_grade_types(entry)
        _validate_grade_range(entry[JC.GRADE])

        student_id = entry[JC.STUDENT_ID]
        topic_id = entry[JC.TOPIC_ID]
        instance_index = entry[JC.INSTANCE]
        grade_value = entry[JC.GRADE]

        student = _get_student(student_id)
        evaluation_instance = _get_evaluation_instance(topic_id, instance_index)
        _check_student_in_section(student, evaluation_instance)
        _check_duplicate_grade(visited_grades, student_id, topic_id, instance_index)

        parsed_grades.append(
            {
                "student_id": student_id,
                "topic_id": topic_id,
                "instance_index": instance_index,
                "grade": grade_value,
            }
        )

    return parsed_grades


def _validate_grade_keys(entry):
    for key in (JC.STUDENT_ID, JC.TOPIC_ID, JC.INSTANCE, JC.GRADE):
        if key not in entry:
            raise ValueError(f"Falta la clave '{key}' en un elemento de '{JC.GRADES}'.")


def _validate_grade_types(entry):
    if not isinstance(entry[JC.STUDENT_ID], int):
        raise ValueError(f"El campo '{JC.STUDENT_ID}' debe ser un número entero.")
    if not isinstance(entry[JC.TOPIC_ID], int):
        raise ValueError(f"El campo '{JC.TOPIC_ID}' debe ser un número entero.")
    if not isinstance(entry[JC.INSTANCE], int):
        raise ValueError(f"El campo '{JC.INSTANCE}' debe ser un número entero.")
    if not isinstance(entry[JC.GRADE], (int, float)):
        raise ValueError(f"El campo '{JC.GRADE}' debe ser un número.")


def _validate_grade_range(grade_value):
    if not 1 <= grade_value <= 7:
        raise ValueError(f"La nota '{grade_value}' no es válida. Debe ser un número entre 1 y 7.")


def _get_student(student_id):
    student = Student.query.filter_by(id=student_id).first()
    if not student:
        raise ValueError(f"No existe un estudiante con ID '{student_id}'.")
    return student


def _get_evaluation_instance(topic_id, instance_index):
    evaluation_instance = EvaluationInstance.query.filter_by(
        evaluation_id=topic_id, index_in_evaluation=instance_index
    ).first()
    if not evaluation_instance:
        raise ValueError(
            f"No existe una instancia de evaluación con evaluación ID "
            f"'{topic_id}' e índice {instance_index}."
        )
    return evaluation_instance


def _check_student_in_section(student, evaluation_instance):
    if evaluation_instance.evaluation.section not in student.sections:
        raise ValueError(
            f"Evaluación {evaluation_instance.title} no es parte de las "
            f"secciones del alumno {student.user.first_name} {student.user.last_name}."
        )


def _check_duplicate_grade(visited_grades, student_id, topic_id, instance_index):
    grade_key = (student_id, topic_id, instance_index)
    if grade_key in visited_grades:
        raise ValueError(
            f"Combinación (student_id, topic_id, instance_index)={grade_key}\
            se encuentra duplicada."
        )
    visited_grades.add(grade_key)

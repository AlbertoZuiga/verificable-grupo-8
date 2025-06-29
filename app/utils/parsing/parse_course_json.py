import json
from collections import defaultdict

from app.models.course import Course
from app.utils import json_constants as JC


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
        for neighbor in graph.get(node, []):
            if neighbor not in visited:
                if dfs(neighbor):
                    return True
            elif neighbor in recursion_stack:
                return True
        recursion_stack.remove(node)
        return False

    return any(dfs(node) for node in graph if node not in visited)

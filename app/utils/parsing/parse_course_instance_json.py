import json
from datetime import datetime

from app.models.course import Course
from app.models.course_instance import CourseInstance, Semester
from app.utils import json_constants as JC


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

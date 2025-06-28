import json

from app.models.section import Section
from app.models.student import Student
from app.models.student_section import StudentSection
from app.utils import json_constants as JC


def validate_required_keys(item):
    if JC.SECTION_ID not in item:
        raise ValueError(
            f"Falta la clave '{JC.SECTION_ID}'\
            en un elemento de '{JC.STUDENT_SECTIONS}'."
        )
    if JC.STUDENT_ID not in item:
        raise ValueError(
            f"Falta la clave '{JC.STUDENT_ID}'\
            en un elemento de '{JC.STUDENT_SECTIONS}'."
        )


def validate_field_types(section_id, student_id):
    if not isinstance(section_id, int):
        raise ValueError(
            f"El campo '{JC.SECTION_ID}' debe ser un número entero\
            en un elemento de '{JC.STUDENT_SECTIONS}'."
        )
    if not isinstance(student_id, int):
        raise ValueError(
            f"El campo '{JC.STUDENT_ID}' debe ser un número entero\
            en un elemento de '{JC.STUDENT_SECTIONS}'."
        )


def validate_no_duplicates(link, visited_links):
    if link in visited_links:
        raise ValueError(
            f"Relación entre estudiante '{link[1]}'\
            y sección '{link[0]}' repetida."
        )
    visited_links.add(link)


def validate_existence(section_id, student_id):
    if not Section.query.filter_by(id=section_id).first():
        raise ValueError(f"No existe una sección con ID '{section_id}'.")
    if not Student.query.filter_by(id=student_id).first():
        raise ValueError(f"No existe un estudiante con ID '{student_id}'.")


def validate_relation_not_exists(section_id, student_id):
    if StudentSection.query.filter_by(section_id=section_id, student_id=student_id).first():
        raise ValueError(
            f"La relación entre estudiante '{student_id}'\
            y sección '{section_id}' ya existe."
        )


def parse_student_sections_json(json_data):
    data = json.loads(json_data)

    if JC.STUDENT_SECTIONS not in data:
        raise ValueError(f"Falta la clave '{JC.STUDENT_SECTIONS}' en el JSON.")

    student_section_data = data[JC.STUDENT_SECTIONS]
    parsed_links = []
    visited_links = set()

    for item in student_section_data:
        validate_required_keys(item)

        section_id = item[JC.SECTION_ID]
        student_id = item[JC.STUDENT_ID]

        validate_field_types(section_id, student_id)

        link = (section_id, student_id)
        validate_no_duplicates(link, visited_links)

        validate_existence(section_id, student_id)

        validate_relation_not_exists(section_id, student_id)

        parsed_links.append(StudentSection(section_id=section_id, student_id=student_id))

    return parsed_links

import json

from app.models.section import Section
from app.models.student import Student
from app.models.student_section import StudentSection
from app.utils import json_constants as JC



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
                f"Relación entre estudiante '{student_id}' y sección '{section_id}' repetida."
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

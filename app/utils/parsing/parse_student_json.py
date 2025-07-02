import json
from datetime import datetime

from app.models.student import Student
from app.models.user import User
from app.utils import json_constants as JC
from app.utils.validation_helpers import validate_id_name_email_types, validate_name_email_format


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
    validate_id_name_email_types(item, JC)

    if not isinstance(item[JC.ENTRY_YEAR], int):
        raise ValueError(f"El campo '{JC.ENTRY_YEAR}' debe ser un número entero.")

    entry_year = item[JC.ENTRY_YEAR]
    if not current_year - 20 <= entry_year <= current_year + 5:
        raise ValueError(
            f"El campo '{JC.ENTRY_YEAR}' debe estar entre {current_year - 20} y {current_year + 5}."
        )

    validate_name_email_format(item[JC.NAME], item[JC.EMAIL])


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

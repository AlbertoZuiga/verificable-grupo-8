import json

from app.models.teacher import Teacher
from app.models.user import User
from app.utils import json_constants as JC
from app.utils.validation_helpers import (validate_id_name_email_types,
                                          validate_name_email_format)


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
    validate_id_name_email_types(item, JC)


def _validate_teacher_field_content(item):
    validate_name_email_format(item[JC.NAME], item[JC.EMAIL])


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

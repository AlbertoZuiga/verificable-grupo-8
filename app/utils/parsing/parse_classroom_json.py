import json

from app.models.classroom import Classroom
from app.utils import json_constants as JC


def validate_required_keys(item):
    for key in (JC.ID, JC.NAME, JC.CAPACITY):
        if key not in item:
            raise ValueError(
                f"Falta la clave '{key}'\
                en un elemento de '{JC.CLASSROOMS}'."
            )


def validate_field_types(item):
    if not isinstance(item[JC.ID], int):
        raise ValueError(
            f"El campo '{JC.ID}' debe ser un número entero\
                en un elemento de '{JC.CLASSROOMS}'."
        )
    if not isinstance(item[JC.NAME], str):
        raise ValueError(
            f"El campo '{JC.NAME}' debe ser una cadena de texto\
                en un elemento de '{JC.CLASSROOMS}'."
        )
    if not isinstance(item[JC.CAPACITY], int):
        raise ValueError(
            f"El campo '{JC.CAPACITY}' debe ser un número entero\
                en un elemento de '{JC.CLASSROOMS}'."
        )


def validate_business_rules(item, ids_seen):
    name = item[JC.NAME]
    if len(name) == 0 or len(name) > 60:
        raise ValueError(
            "El largo del nombre debe ser mayor que 0 y menor o igual que 60 caracteres."
        )

    capacity = item[JC.CAPACITY]
    if capacity < 0 or capacity > 1000:
        raise ValueError("La capacidad debe ser mayor o igual a 0 y menor o igual que 1000.")

    if item[JC.ID] in ids_seen:
        raise ValueError(f"ID duplicado '{item[JC.ID]}' encontrado en '{JC.CLASSROOMS}'.")
    ids_seen.add(item[JC.ID])


def parse_classrooms_json(json_data):
    classrooms = []
    data = json.loads(json_data)

    if JC.CLASSROOMS not in data:
        raise ValueError(f"Falta la clave '{JC.CLASSROOMS}' en el JSON.")

    json_dictionary = data[JC.CLASSROOMS]
    ids_seen = set()

    for item in json_dictionary:
        validate_required_keys(item)
        validate_field_types(item)
        validate_business_rules(item, ids_seen)

        classroom = Classroom(
            id=item[JC.ID],
            name=item[JC.NAME],
            capacity=item[JC.CAPACITY],
        )
        classrooms.append(classroom)

    return classrooms

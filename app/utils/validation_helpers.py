import re


def validate_id_name_email_types(item, constants):
    if not isinstance(item[constants.NAME], str):
        raise ValueError(f"El campo '{constants.NAME}' debe ser una cadena de texto.")
    if not isinstance(item[constants.EMAIL], str):
        raise ValueError(f"El campo '{constants.EMAIL}' debe ser una cadena de texto.")
    if not isinstance(item[constants.ID], int):
        raise ValueError(f"El campo '{constants.ID}' debe ser un número entero.")


def validate_name_email_format(name, email):
    if not 0 < len(name) <= 60:
        raise ValueError(
            "El largo del nombre debe ser mayor que 0\
            y menor o igual que 60 caracteres."
        )
    if not 0 < len(email) <= 60:
        raise ValueError(
            "El largo del correo debe ser mayor que 0\
            y menor o igual que 60 caracteres."
        )

    email_regex = r"^[\w\.-]+@[\w\.-]+\.\w+$"
    if not re.match(email_regex, email):
        raise ValueError(f"El correo '{email}' no tiene un formato válido.")

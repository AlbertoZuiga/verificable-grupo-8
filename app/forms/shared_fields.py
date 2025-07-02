from wtforms import StringField
from wtforms.validators import DataRequired, Email, Length, NoneOf


class SharedUserFields:
    first_name = StringField(
        "Nombre",
        validators=[
            DataRequired("Nombre debe estar presente"),
            Length(max=60, message="Nombre debe tener maximo 60 caracteres"),
        ],
    )
    last_name = StringField(
        "Apellido",
        validators=[
            DataRequired("Apellido debe estar presente"),
            Length(max=60, message="Apellido debe tener maximo 60 caracteres"),
        ],
    )
    email = StringField(
        "Correo electrónico",
        validators=[
            DataRequired("Correo debe estar presente."),
            Email(),
            Length(max=60, message="Correo debe tener maximo 60 caracteres"),
            NoneOf([], message="Correo ya esta registrado por otro usuario."),
        ],
    )

from datetime import datetime

from flask_wtf import FlaskForm
from wtforms import IntegerField, PasswordField, StringField, SubmitField
from wtforms.validators import DataRequired, Email, Length, NoneOf, NumberRange

current_year = datetime.now().year


class StudentCreateForm(FlaskForm):
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
    university_entry_year = IntegerField(
        "Año de ingreso",
        validators=[
            DataRequired("Año de ingreso debe estar presente"),
            NumberRange(
                min=current_year - 20,
                max=current_year + 5,
                message=f"Año debe estar entre {current_year - 20} y {current_year + 5}",
            ),
        ],
    )
    password = PasswordField(
        "Contraseña",
        validators=[DataRequired("Contraseña debe estar presente")],
    )
    submit = SubmitField("Guardar")


class StudentEditForm(FlaskForm):
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
    university_entry_year = IntegerField(
        "Año de ingreso",
        validators=[
            DataRequired("Año de ingreso debe estar presente"),
            NumberRange(
                min=current_year - 20,
                max=current_year + 5,
                message=f"Año debe estar entre {current_year - 20} y {current_year + 5}",
            ),
        ],
    )
    submit = SubmitField("Guardar")

    def __init__(self, original_email, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.original_email = original_email

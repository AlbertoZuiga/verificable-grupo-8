from datetime import datetime

from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, SubmitField
from wtforms.validators import DataRequired, Email, Length, NoneOf

current_year = datetime.now().year


class TeacherCreateForm(FlaskForm):
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
    password = PasswordField(
        "Contraseña",
        validators=[DataRequired("Contraseña debe estar presente")],
    )
    submit = SubmitField("Guardar")


class TeacherEditForm(FlaskForm):
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
    submit = SubmitField("Guardar")

    def __init__(self, original_email, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.original_email = original_email

from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, SubmitField
from wtforms.validators import DataRequired, Email, Length


class UserForm(FlaskForm):
    first_name = StringField(
        "Nombre",
        validators=[
            DataRequired("Nombre debe estar presente"),
            Length(
                min=2,
                max=60,
                message="Nombre debe tener minimo 2 caracteres y maximo 60",
            ),
        ],
    )
    last_name = StringField(
        "Apellido",
        validators=[
            DataRequired("Apellido debe estar presente"),
            Length(
                min=2,
                max=60,
                message="Apellido debe tener minimo 2 caracteres y maximo 60",
            ),
        ],
    )
    email = StringField(
        "Correo electrónico",
        validators=[DataRequired("Email debe estar presente."), Email()],
    )
    password = PasswordField("Contraseña", validators=[Length(min=6, max=60)])
    submit = SubmitField("💾 Guardar")


class EditUserForm(FlaskForm):
    first_name = StringField(
        "Nombre",
        validators=[
            DataRequired("Nombre debe estar presente"),
            Length(
                min=2,
                max=60,
                message="Nombre debe tener minimo 2 caracteres y maximo 60",
            ),
        ],
    )
    last_name = StringField(
        "Apellido",
        validators=[
            DataRequired("Apellido debe estar presente"),
            Length(
                min=2,
                max=60,
                message="Apellido debe tener minimo 2 caracteres y maximo 60",
            ),
        ],
    )
    email = StringField(
        "Correo electrónico",
        validators=[DataRequired("Email debe estar presente."), Email()],
    )
    submit = SubmitField("💾 Guardar")

from datetime import datetime

from flask_wtf import FlaskForm
from wtforms import PasswordField, SubmitField
from wtforms.validators import DataRequired

from app.forms.shared_fields import SharedUserFields

current_year = datetime.now().year


class CreateUserForm(FlaskForm, SharedUserFields):
    password = PasswordField(
        "Contraseña",
        validators=[DataRequired("Contraseña debe estar presente")],
    )
    submit = SubmitField("Guardar")


class EditUserForm(FlaskForm, SharedUserFields):
    submit = SubmitField("Guardar")

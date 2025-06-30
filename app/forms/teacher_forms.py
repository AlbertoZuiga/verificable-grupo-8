from datetime import datetime

from flask_wtf import FlaskForm
from wtforms import PasswordField, SubmitField
from wtforms.validators import DataRequired

from app.forms.shared_fields import SharedUserFields

current_year = datetime.now().year


class TeacherCreateForm(FlaskForm, SharedUserFields):
    password = PasswordField(
        "Contraseña",
        validators=[DataRequired("Contraseña debe estar presente")],
    )
    submit = SubmitField("Guardar")


class TeacherEditForm(FlaskForm, SharedUserFields):
    submit = SubmitField("Guardar")

    def __init__(self, original_email, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.original_email = original_email

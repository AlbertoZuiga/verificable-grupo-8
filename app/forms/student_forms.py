from datetime import datetime

from flask_wtf import FlaskForm
from wtforms import IntegerField, PasswordField, SubmitField
from wtforms.validators import DataRequired, NumberRange

from app.forms.shared_fields import SharedUserFields

current_year = datetime.now().year


class CreateStudentForm(FlaskForm, SharedUserFields):
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


class EditStudentForm(FlaskForm, SharedUserFields):
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

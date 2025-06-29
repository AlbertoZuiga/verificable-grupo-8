from datetime import datetime

from flask_wtf import FlaskForm
from wtforms import IntegerField, SelectField
from wtforms.validators import AnyOf, DataRequired, NumberRange

from app.models.course_instance import Semester

current_year = datetime.now().year


class CourseInstanceForm(FlaskForm):
    course_id = SelectField(
        "Curso",
        coerce=int,
        validators=[DataRequired(message="El curso es obligatorio.")],
    )
    year = IntegerField(
        "Año",
        validators=[
            DataRequired(message="El año es obligatorio."),
            NumberRange(
                min=current_year - 5,
                max=current_year + 5,
                message=f"El año debe estar entre {current_year-5} y {current_year+5}.",
            ),
        ],
    )
    semester = SelectField(
        "Semestre",
        choices=[(member.name, member.name.capitalize()) for member in Semester],
        validators=[
            DataRequired(message="El semestre es obligatorio."),
            AnyOf(
                [member.name for member in Semester],
                message="El semestre seleccionado no es válido.",
            ),
        ],
    )

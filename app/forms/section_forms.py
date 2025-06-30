from flask_wtf import FlaskForm
from wtforms import IntegerField, SelectField, SubmitField
from wtforms.validators import AnyOf, DataRequired, NumberRange

from app.models.section import WeighingType


class SectionForm(FlaskForm):
    course_instance_id = SelectField(
        "Instancia del Curso",
        coerce=int,
        validators=[
            DataRequired("Instancia de curso debe estar presente."),
            AnyOf([], message="Debes seleccionar una instancia de curso valida."),
        ],
    )
    teacher_id = SelectField(
        "Profesor",
        coerce=int,
        validators=[
            DataRequired("Profesor debe estar presente."),
            AnyOf([], message="Debes seleccionar una profesor valido."),
        ],
    )
    code = IntegerField(
        "Código de Sección",
        validators=[
            DataRequired("Codigo debe estar presente."),
            NumberRange(min=1, max=5000, message="Debe ser un numero entre 1 y 5000."),
        ],
    )
    weighing_type = SelectField(
        "Tipo de Ponderación",
        choices=[(type.name, type.value) for type in WeighingType],
        validators=[DataRequired("Tipo de ponderacion debe estar presente.")],
    )
    submit = SubmitField("Crear")

from flask_wtf import FlaskForm
from wtforms import SelectField, StringField, SubmitField
from wtforms.validators import AnyOf, DataRequired, Length

from app.models.section import WeighingType


class EvaluationForm(FlaskForm):
    section_id = SelectField(
        "Sección",
        validators=[
            DataRequired(message="Debes seleccionar una sección."),
            AnyOf([], message="Debes seleccionar una sección valida"),
        ],
        coerce=int,
    )
    title = StringField(
        "Título de la Evaluación",
        validators=[
            DataRequired(message="El título es obligatorio."),
            Length(max=60, message="El título no puede superar los 60 caracteres."),
        ],
    )

    weighing_system = SelectField(
        "Sistema de Ponderación",
        choices=[(type.name, type.value) for type in WeighingType],
        validators=[
            DataRequired(message="Debes seleccionar un sistema de ponderación."),
            AnyOf([type.name for type in WeighingType], message="Sistema de ponderación inválido."),
        ],
    )
    submit = SubmitField("💾 Guardar Cambios")

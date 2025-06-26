from flask_wtf import FlaskForm
from wtforms import SelectField, StringField, SubmitField
from wtforms.validators import DataRequired, Length

from app.models.section import WeighingType


class EvaluationForm(FlaskForm):
    section_id = SelectField("Sección", validators=[DataRequired()], coerce=int)
    title = StringField("Título de la Evaluación", validators=[DataRequired(), Length(max=60)])
    weighing_system = SelectField(
        "Sistema de Ponderación",
        choices=[(type.name, type.value) for type in WeighingType],
        validators=[DataRequired()],
    )
    submit = SubmitField("💾 Guardar Cambios")

from flask_wtf import FlaskForm
from wtforms import SelectField, IntegerField, SubmitField
from wtforms.validators import DataRequired, NumberRange

from app.models.section import WeighingType

class SectionForm(FlaskForm):
    course_instance_id = SelectField('Instancia del Curso', coerce=int, validators=[DataRequired()])
    teacher_id = SelectField('Profesor', coerce=int, validators=[DataRequired()])
    code = IntegerField('Código de Sección', validators=[DataRequired(), NumberRange(min=1, max=5000)])
    weighing_type = SelectField(
        "Tipo de Ponderación",
        choices = [(type.name, type.value) for type in WeighingType],
        validators=[DataRequired()]
    )
    submit = SubmitField('Crear')
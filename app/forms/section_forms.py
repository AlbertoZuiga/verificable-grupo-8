from flask_wtf import FlaskForm
from wtforms import SelectField, IntegerField, SubmitField
from wtforms.validators import DataRequired, NumberRange

class SectionForm(FlaskForm):
    course_instance_id = SelectField('Instancia del Curso', coerce=int, validators=[DataRequired()])
    teacher_id = SelectField('Profesor', coerce=int, validators=[DataRequired()])
    code = IntegerField('Código de Sección', validators=[DataRequired(), NumberRange(min=1)])
    weighing_type = SelectField('Tipo de Ponderación', validators=[DataRequired()])
    submit = SubmitField('Crear')
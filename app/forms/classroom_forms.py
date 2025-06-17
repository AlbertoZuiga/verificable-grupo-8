from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SubmitField
from wtforms.validators import DataRequired, NumberRange

class ClassroomForm(FlaskForm):
    name = StringField('Nombre de la Sala', validators=[DataRequired()])
    capacity = IntegerField('Capacidad', validators=[DataRequired(), NumberRange(min=1)])
    submit = SubmitField('Crear')
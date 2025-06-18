from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SubmitField
from wtforms.validators import DataRequired, NumberRange, Length

class ClassroomForm(FlaskForm):
    name = StringField('Nombre de la Sala', validators=[DataRequired(), Length(max=60)])
    capacity = IntegerField('Capacidad', validators=[DataRequired(), NumberRange(min=1, max=1000)])
    submit = SubmitField('Crear')
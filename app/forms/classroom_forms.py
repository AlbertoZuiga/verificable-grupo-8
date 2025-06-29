from flask_wtf import FlaskForm
from wtforms import IntegerField, StringField, SubmitField
from wtforms.validators import DataRequired, Length, NumberRange


class ClassroomForm(FlaskForm):
    name = StringField(
        "Nombre de la Sala",
        validators=[
            DataRequired(message="Este campo es obligatorio."),
            Length(max=60, message="Este campo debe tener como maximo 60 caracteres."),
        ],
    )
    capacity = IntegerField(
        "Capacidad",
        validators=[
            DataRequired(message="Este campo es obligatorio."),
            NumberRange(min=1, max=1000, message="Debe estar entre 1 y 1000."),
        ],
    )
    submit = SubmitField("Crear")

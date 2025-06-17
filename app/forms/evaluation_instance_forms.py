from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length
from app.models import Evaluation

class EvaluationInstanceForm(FlaskForm):
    title = StringField("Título de la Instancia de Evaluación", validators=[DataRequired(), Length(max=60)])
    evaluation_id = SelectField("Evaluación", coerce=int, validators=[DataRequired()])
    optional = BooleanField("¿Es opcional?")
    submit = SubmitField("💾 Guardar Cambios")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.evaluation_id.choices = [
            (e.id, f"{e.title} - {e.section.course_instance.course.title}")
            for e in Evaluation.query.all()
        ]
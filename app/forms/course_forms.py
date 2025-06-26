from flask_wtf import FlaskForm
from wtforms import IntegerField, StringField
from wtforms.validators import DataRequired, Length, NumberRange


class CourseForm(FlaskForm):
    title = StringField("Título", validators=[DataRequired(), Length(max=60)])
    code = StringField("Código", validators=[DataRequired(), Length(max=15)])
    credits = IntegerField(
        "Créditos", validators=[DataRequired(), NumberRange(min=0, max=20)]
    )

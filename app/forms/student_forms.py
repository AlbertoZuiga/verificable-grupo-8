from datetime import datetime

from flask_wtf import FlaskForm
from wtforms import IntegerField, PasswordField, StringField, SubmitField
from wtforms.validators import (DataRequired, Email, Length, NumberRange,
                                ValidationError)

from app.models import User

current_year = datetime.now().year


class StudentCreateForm(FlaskForm):
    first_name = StringField("Nombre", validators=[DataRequired(), Length(max=60)])
    last_name = StringField("Apellido", validators=[DataRequired(), Length(max=60)])
    email = StringField("Correo electrónico", validators=[DataRequired(), Email(), Length(max=60)])
    university_entry_year = IntegerField(
        "Año de ingreso",
        validators=[
            DataRequired(),
            NumberRange(min=current_year - 20, max=current_year + 5),
        ],
    )
    password = PasswordField("Contraseña", validators=[DataRequired()])
    submit = SubmitField("Guardar")

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError("El correo electrónico ya está registrado.")


class StudentEditForm(FlaskForm):
    first_name = StringField("Nombre", validators=[DataRequired(), Length(max=60)])
    last_name = StringField("Apellido", validators=[DataRequired(), Length(max=60)])
    email = StringField("Correo electrónico", validators=[DataRequired(), Email(), Length(max=60)])
    university_entry_year = IntegerField(
        "Año de ingreso",
        validators=[
            DataRequired(),
            NumberRange(min=current_year - 20, max=current_year + 5),
        ],
    )
    submit = SubmitField("Guardar")

    def __init__(self, original_email, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.original_email = original_email

    def validate_email(self, email):
        if email.data != self.original_email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError("El correo electrónico ya está registrado por otro usuario.")

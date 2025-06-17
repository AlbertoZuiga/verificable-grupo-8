from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, ValidationError
from app.models import User

class TeacherCreateForm(FlaskForm):
    first_name = StringField('Nombre', validators=[DataRequired()])
    last_name = StringField('Apellido', validators=[DataRequired()])
    email = StringField('Correo electrónico', validators=[DataRequired(), Email()])
    password = PasswordField('Contraseña', validators=[DataRequired()])
    submit = SubmitField('💾 Guardar')

    def validate_email(self, email):
        if User.query.filter_by(email=email.data).first():
            raise ValidationError('El correo electrónico ya está registrado.')

class TeacherEditForm(FlaskForm):
    first_name = StringField('Nombre', validators=[DataRequired()])
    last_name = StringField('Apellido', validators=[DataRequired()])
    email = StringField('Correo electrónico', validators=[DataRequired(), Email()])
    submit = SubmitField('💾 Guardar')

    def __init__(self, original_email, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.original_email = original_email

    def validate_email(self, email):
        if email.data != self.original_email:
            if User.query.filter_by(email=email.data).first():
                raise ValidationError('El correo electrónico ya está registrado por otro usuario.')
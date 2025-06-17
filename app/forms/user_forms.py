from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, Length

class UserForm(FlaskForm):
    first_name = StringField('Nombre', validators=[DataRequired(), Length(min=2, max=60)])
    last_name = StringField('Apellido', validators=[DataRequired(), Length(min=2, max=60)])
    email = StringField('Correo electrónico', validators=[DataRequired(), Email()])
    password = PasswordField('Contraseña', validators=[Length(min=6)])
    submit = SubmitField('💾 Guardar')

class EditUserForm(FlaskForm):
    first_name = StringField('Nombre', validators=[DataRequired(), Length(min=2, max=60)])
    last_name = StringField('Apellido', validators=[DataRequired(), Length(min=2, max=60)])
    email = StringField('Correo electrónico', validators=[DataRequired(), Email()])
    submit = SubmitField('💾 Guardar')
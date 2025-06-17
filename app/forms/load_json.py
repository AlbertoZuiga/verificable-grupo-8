from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import HiddenField, SubmitField, ValidationError

from app.utils import json_constants as JC

class UploadJSONForm(FlaskForm):
    file = FileField('Selecciona un archivo JSON:', validators=[
        FileRequired(),
        FileAllowed(['json'], 'Solo archivos JSON permitidos.')
    ])
    json_type = HiddenField()
    submit = SubmitField('Subir')

    allowed_types = {
        JC.STUDENTS,
        JC.TEACHERS,
        JC.CLASSROOMS,
        JC.COURSES,
        JC.COURSE_INSTANCES,
        JC.SECTIONS,
        JC.STUDENT_SECTIONS,
        JC.GRADES,
    }

    def validate_json_type(form, field):
        if field.data not in form.allowed_types:
            raise ValidationError('Tipo de JSON inválido.')
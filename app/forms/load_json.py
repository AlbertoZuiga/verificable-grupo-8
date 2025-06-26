import json

from flask import request
from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileField, FileRequired
from wtforms import HiddenField, SubmitField, ValidationError

from app.utils import json_constants as JC

MAX_FILE_SIZE = 2 * 1024 * 1024


def validate_file_size(_):
    if request.content_length > MAX_FILE_SIZE:
        raise ValidationError("El archivo excede el tamaño máximo permitido (2MB).")


def validate_file(form, field):
    file_data = field.data
    try:
        file_bytes = file_data.read()
        file_data.seek(0)

        try:
            file_contents = file_bytes.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise ValidationError(
                "El archivo no está codificado en UTF-8 o no es texto válido."
            ) from exc

        data = json.loads(file_contents)

        if form.json_type.data not in UploadJSONForm.allowed_types:
            raise ValidationError("Tipo de JSON inválido.")

        if not isinstance(data, dict):
            raise ValidationError("El archivo JSON debe tener un objeto como estructura principal.")

    except json.JSONDecodeError as exc:
        raise ValidationError("El contenido del archivo no es un JSON válido.") from exc


class UploadJSONForm(FlaskForm):
    file = FileField(
        "Selecciona un archivo JSON:",
        validators=[
            FileRequired(),
            FileAllowed(["json"], "Solo archivos JSON permitidos."),
            validate_file_size,
            validate_file,
        ],
    )
    json_type = HiddenField()
    submit = SubmitField("Subir")

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

    def validate_json_type(self, field):
        if field.data not in self.allowed_types:
            raise ValidationError("Tipo de JSON inválido.")

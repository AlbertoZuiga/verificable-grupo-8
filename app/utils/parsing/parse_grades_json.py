import json

from app.models.evaluation_instance import EvaluationInstance
from app.models.student import Student
from app.utils import json_constants as JC

def parse_grades_json(json_data):
    data = json.loads(json_data)

    if JC.GRADES not in data:
        raise ValueError(f"Falta la clave '{JC.GRADES}' en el JSON.")

    grades_raw = data[JC.GRADES]
    parsed_grades = []
    visited_grades = set()

    for entry in grades_raw:
        _validate_grade_keys(entry)
        _validate_grade_types(entry)
        _validate_grade_range(entry[JC.GRADE])

        student_id = entry[JC.STUDENT_ID]
        topic_id = entry[JC.TOPIC_ID]
        instance_index = entry[JC.INSTANCE]
        grade_value = entry[JC.GRADE]

        student = _get_student(student_id)
        evaluation_instance = _get_evaluation_instance(topic_id, instance_index)
        _check_student_in_section(student, evaluation_instance)
        _check_duplicate_grade(visited_grades, student_id, topic_id, instance_index)

        parsed_grades.append(
            {
                "student_id": student_id,
                "topic_id": topic_id,
                "instance_index": instance_index,
                "grade": grade_value,
            }
        )

    return parsed_grades

def _validate_grade_keys(entry):
    for key in (JC.STUDENT_ID, JC.TOPIC_ID, JC.INSTANCE, JC.GRADE):
        if key not in entry:
            raise ValueError(f"Falta la clave '{key}' en un elemento de '{JC.GRADES}'.")


def _validate_grade_types(entry):
    if not isinstance(entry[JC.STUDENT_ID], int):
        raise ValueError(f"El campo '{JC.STUDENT_ID}' debe ser un número entero.")
    if not isinstance(entry[JC.TOPIC_ID], int):
        raise ValueError(f"El campo '{JC.TOPIC_ID}' debe ser un número entero.")
    if not isinstance(entry[JC.INSTANCE], int):
        raise ValueError(f"El campo '{JC.INSTANCE}' debe ser un número entero.")
    if not isinstance(entry[JC.GRADE], (int, float)):
        raise ValueError(f"El campo '{JC.GRADE}' debe ser un número.")


def _validate_grade_range(grade_value):
    if not 1 <= grade_value <= 7:
        raise ValueError(f"La nota '{grade_value}' no es válida. Debe ser un número entre 1 y 7.")


def _get_student(student_id):
    student = Student.query.filter_by(id=student_id).first()
    if not student:
        raise ValueError(f"No existe un estudiante con ID '{student_id}'.")
    return student


def _get_evaluation_instance(topic_id, instance_index):
    evaluation_instance = EvaluationInstance.query.filter_by(
        evaluation_id=topic_id, index_in_evaluation=instance_index
    ).first()
    if not evaluation_instance:
        raise ValueError(
            f"No existe una instancia de evaluación con evaluación ID "
            f"'{topic_id}' e índice {instance_index}."
        )
    return evaluation_instance


def _check_student_in_section(student, evaluation_instance):
    if evaluation_instance.evaluation.section not in student.sections:
        raise ValueError(
            f"Evaluación {evaluation_instance.title} no es parte de las "
            f"secciones del alumno {student.user.first_name} {student.user.last_name}."
        )


def _check_duplicate_grade(visited_grades, student_id, topic_id, instance_index):
    grade_key = (student_id, topic_id, instance_index)
    if grade_key in visited_grades:
        raise ValueError(
            f"Combinación (student_id, topic_id, instance_index)={grade_key}\
            se encuentra duplicada."
        )
    visited_grades.add(grade_key)

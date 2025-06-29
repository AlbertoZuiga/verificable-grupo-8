from flask import Blueprint, redirect, render_template, request, url_for
from sqlalchemy.exc import SQLAlchemyError

from app.extensions import kanvas_db
from app.models.evaluation_instance import EvaluationInstance
from app.models.student_evaluation_instance import StudentEvaluationInstance
from app.services.validations import validate_section_for_evaluation

grade_bp = Blueprint("grades", __name__, url_prefix="/grades")


def _get_section_id(evaluation_instance_id):
    """Obtiene el ID de sección desde una instancia de evaluación."""
    instance = EvaluationInstance.query.get_or_404(evaluation_instance_id)
    return instance.evaluation.section.id


def _get_evaluation_context(evaluation_instance_id, student_id=None):
    """Obtiene contexto base para operaciones con evaluaciones."""
    instance = EvaluationInstance.query.get_or_404(evaluation_instance_id)

    if student_id:
        student = next(
            (s for s in instance.evaluation.section.students if s.id == student_id), None
        )
        return instance, student

    return instance


def _get_student_grade(evaluation_instance_id, student_id):
    """Obtiene la calificación de un estudiante si existe."""
    return StudentEvaluationInstance.query.filter_by(
        evaluation_instance_id=evaluation_instance_id, student_id=student_id
    ).first()


def _save_grade_transaction(evaluation_instance_id, student_id, grade_value):
    """Guarda o actualiza una calificación en transacción segura."""
    try:
        grade_instance = _get_student_grade(evaluation_instance_id, student_id)

        if grade_instance:
            grade_instance.grade = grade_value
        else:
            new_grade = StudentEvaluationInstance(
                student_id=student_id,
                evaluation_instance_id=evaluation_instance_id,
                grade=grade_value,
            )
            kanvas_db.session.add(new_grade)

        kanvas_db.session.commit()
        return True
    except SQLAlchemyError as e:
        kanvas_db.session.rollback()
        raise e


def _validate_section(evaluation_instance_id):
    """Valida los permisos sobre la sección asociada."""
    section_id = _get_section_id(evaluation_instance_id)
    return validate_section_for_evaluation(section_id)


def _handle_grade_error(exception, action_message):
    """Maneja errores durante operaciones con calificaciones."""
    print(f"Error al {action_message}: {exception}")
    return f"Error al {action_message}", 500


def _redirect_to_evaluation(evaluation_instance_id):
    """Redirige a la vista de instancia de evaluación."""
    return redirect(
        url_for("evaluation_instance.show", evaluation_instance_id=evaluation_instance_id)
    )


@grade_bp.route("/<int:evaluation_instance_id>/student/<int:student_id>", methods=["GET", "POST"])
def assign_or_edit_grade(evaluation_instance_id, student_id):
    """Asigna o edita una calificación para un estudiante."""
    if error := _validate_section(evaluation_instance_id):
        return error

    instance, student = _get_evaluation_context(evaluation_instance_id, student_id)

    if not student:
        return "Estudiante no pertenece a esta sección", 404

    if request.method == "POST":
        return _handle_grade_submission(evaluation_instance_id, student_id)

    return _render_grade_form(instance, student, evaluation_instance_id)


def _handle_grade_submission(evaluation_instance_id, student_id):
    """Procesa el envío del formulario de calificación."""
    grade_input = request.form.get("grade", "").strip()

    if not grade_input:
        return "Nota vacía", 400

    try:
        grade_value = float(grade_input)
        _save_grade_transaction(evaluation_instance_id, student_id, grade_value)
        return _redirect_to_evaluation(evaluation_instance_id)
    except (ValueError, SQLAlchemyError) as e:
        return _handle_grade_error(e, "guardar la nota")


def _render_grade_form(instance, student, evaluation_instance_id):
    """Renderiza el formulario de calificación."""
    grade_instance = _get_student_grade(evaluation_instance_id, student.id)
    current_grade = grade_instance.grade if grade_instance else None

    return render_template(
        "evaluation_instances/grade_user.html",
        evaluation_instance=instance,
        student=student,
        current_grade=current_grade,
    )


@grade_bp.route("/<int:evaluation_instance_id>/delete/<int:student_id>", methods=["POST"])
def delete_grade(evaluation_instance_id, student_id):
    """Elimina una calificación existente."""
    if error := _validate_section(evaluation_instance_id):
        return error

    grade_instance = _get_student_grade(evaluation_instance_id, student_id)

    if not grade_instance:
        return "Nota no encontrada", 404

    try:
        kanvas_db.session.delete(grade_instance)
        kanvas_db.session.commit()
        return _redirect_to_evaluation(evaluation_instance_id)
    except SQLAlchemyError as e:
        return _handle_grade_error(e, "eliminar la nota")

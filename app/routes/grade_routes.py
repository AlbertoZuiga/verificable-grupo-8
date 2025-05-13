from flask import Blueprint, render_template, request, redirect, url_for
from app import kanvas_db
from app.services.evaluation_instance_service import (
    get_evaluation_instance_and_student,
    get_student_grade_instance,
    save_student_grade
)

grade_bp = Blueprint('grades', __name__, url_prefix='/grades')


@grade_bp.route('/<int:evaluation_instance_id>/assign/<int:student_id>', methods=['GET', 'POST'])
def assign_or_edit_grade(evaluation_instance_id, student_id):
    evaluation_instance, student = get_evaluation_instance_and_student(evaluation_instance_id, student_id)

    if not student:
        return "Estudiante no pertenece a esta sección", 404

    current_grade_instance = get_student_grade_instance(evaluation_instance_id, student_id)
    current_grade = current_grade_instance.grade if current_grade_instance else None

    if request.method == 'POST':
        grade_input = request.form.get('grade')

        if not grade_input or grade_input.strip() == "":
            return "Nota vacía", 400

        try:
            grade_value = float(grade_input)
        except ValueError:
            return "Nota inválida", 400

        try:
            save_student_grade(evaluation_instance_id, student_id, grade_value)
            return redirect(url_for('evaluation_instance.show', id=evaluation_instance_id))
        except Exception as e:
            kanvas_db.session.rollback()
            print(f"Error al guardar la nota: {e}")
            return "Error al guardar la nota", 500

    return render_template(
        'evaluation_instances/grade_user.html',
        evaluation_instance=evaluation_instance,
        student=student,
        current_grade=current_grade
    )


@grade_bp.route('/<int:evaluation_instance_id>/delete/<int:student_id>', methods=['POST'])
def delete_grade(evaluation_instance_id, student_id):
    grade_instance = get_student_grade_instance(evaluation_instance_id, student_id)

    if not grade_instance:
        return "Nota no encontrada", 404

    try:
        kanvas_db.session.delete(grade_instance)
        kanvas_db.session.commit()
        return redirect(url_for('evaluation_instance.show', id=evaluation_instance_id))
    except Exception as e:
        kanvas_db.session.rollback()
        print(f"Error al eliminar la nota: {e}")
        return "Error al eliminar la nota", 500

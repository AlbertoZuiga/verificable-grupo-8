from flask import Blueprint, render_template, request, redirect, url_for
from app import kanvas_db
from app.models import EvaluationInstance, Evaluation
from app.services.evaluation_instance_service import (
    get_evaluation_instance_with_students_and_grades,
    get_evaluation_instance_and_student,
    get_student_grade_instance,
    save_student_grade
)

evaluation_instance_bp = Blueprint('evaluation_instance', __name__, url_prefix='/evaluation_instances')


@evaluation_instance_bp.route('/')
def index():
    evaluation_instances = EvaluationInstance.query.all()
    return render_template('evaluation_instances/index.html', evaluation_instances=evaluation_instances)


@evaluation_instance_bp.route('/<int:id>')
def show(id):
    evaluation_instance, students, student_grades = get_evaluation_instance_with_students_and_grades(id)
    return render_template(
        'evaluation_instances/show.html',
        evaluation_instance=evaluation_instance,
        students=students,
        student_grades=student_grades
    )


@evaluation_instance_bp.route('/create', methods=['GET', 'POST'])
def create():
    if request.method == 'POST':
        title = request.form['title']
        instance_weighing = request.form['instance_weighing']
        optional = request.form.get("optional") == "on"
        evaluation_id = request.form['evaluation_id']
        
        if Evaluation.query.get(evaluation_id) is None:
            return "Invalid evaluation ID", 400

        evaluation_instance = EvaluationInstance(
            title=title,
            instance_weighing=instance_weighing,
            optional=optional,
            evaluation_id=evaluation_id
        )

        try:
            kanvas_db.session.add(evaluation_instance)
            kanvas_db.session.commit()
            return redirect(url_for('evaluation_instance.show', id=evaluation_instance.id))
        except Exception as e:
            kanvas_db.session.rollback()
            print(f"Error creating evaluation_instance: {e}")
    
    evaluations = Evaluation.query.all()
    return render_template('evaluation_instances/create.html', evaluations=evaluations)


@evaluation_instance_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    evaluation_instance = EvaluationInstance.query.get_or_404(id)

    if request.method == 'POST':
        evaluation_instance.title = request.form['title']
        evaluation_instance.instance_weighing = request.form['instance_weighing']
        evaluation_instance.optional = request.form.get("optional") == "on"
        evaluation_id = request.form['evaluation_id']

        if Evaluation.query.get(evaluation_id) is None:
            return "Invalid evaluation ID", 400

        evaluation_instance.evaluation_id = evaluation_id

        try:
            kanvas_db.session.commit()
            return redirect(url_for('evaluation_instance.show', id=evaluation_instance.id))
        except Exception as e:
            kanvas_db.session.rollback()
            print(f"Error updating evaluation_instance: {e}")
    
    evaluations = Evaluation.query.all()
    return render_template('evaluation_instances/edit.html', evaluation_instance=evaluation_instance, evaluations=evaluations)


@evaluation_instance_bp.route('/delete/<int:id>')
def delete(id):
    evaluation_instance = EvaluationInstance.query.get_or_404(id)
    try:
        kanvas_db.session.delete(evaluation_instance)
        kanvas_db.session.commit()
    except Exception as e:
        kanvas_db.session.rollback()
        print(f"Error deleting evaluation_instance: {e}")
    return redirect(url_for('evaluation_instance.index'))


@evaluation_instance_bp.route('/<int:evaluation_instance_id>/grade/<int:student_id>', methods=['GET', 'POST'])
def grade_user(evaluation_instance_id, student_id):
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

@evaluation_instance_bp.route('/<int:evaluation_instance_id>/delete_grade/<int:student_id>', methods=['POST'])
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

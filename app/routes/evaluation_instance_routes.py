from flask import Blueprint, render_template, request, redirect, url_for, flash
from app import kanvas_db
from app.models import EvaluationInstance, Evaluation, Section
from app.services.evaluation_instance_service import (
    get_evaluation_instance_with_students_and_grades,
    get_section_id
)
from app.services.decorators import require_section_open
from app.services.validations import validate_section_for_evaluation

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
        optional = request.form.get("optional") == "on"
        evaluation_id = request.form['evaluation_id']
        
        evaluation = Evaluation.query.get_or_404(evaluation_id)
        if evaluation is None:
            flash("Invalid evaluation ID", "danger")
            return redirect(url_for('evaluation_instance.create'))

        section_id = get_section_id(evaluation_id)

        validation_error = validate_section_for_evaluation(section_id)
        if validation_error:
            return validation_error
        
        evaluation_instance = EvaluationInstance(
            title=title,
            instance_weighing=0.0,
            optional=optional,
            evaluation_id=evaluation_id,
            index_in_evaluation=len(evaluation.instances) + 1,
        )

        try:
            kanvas_db.session.add(evaluation_instance)
            kanvas_db.session.commit()
            return redirect(url_for('evaluation_instance.show', id=evaluation_instance.id))
        except Exception as e:
            kanvas_db.session.rollback()
            flash(f"Error creating evaluation_instance: {e}", "danger")

    evaluations = Evaluation.query.all()
    return render_template('evaluation_instances/create.html', evaluations=evaluations)


@evaluation_instance_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
@require_section_open(lambda id: Evaluation.query.get_or_404(id).section) 
def edit(id):
    evaluation_instance = EvaluationInstance.query.get_or_404(id)

    if request.method == 'POST':
        evaluation_instance.title = request.form['title']
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
@require_section_open(lambda id: Evaluation.query.get_or_404(id).section)
def delete(id):
    evaluation_instance = EvaluationInstance.query.get_or_404(id)
    try:
        kanvas_db.session.delete(evaluation_instance)
        kanvas_db.session.commit()
    except Exception as e:
        kanvas_db.session.rollback()
        print(f"Error deleting evaluation_instance: {e}")
    return redirect(url_for('evaluation_instance.index'))

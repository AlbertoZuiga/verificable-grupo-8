from flask import Blueprint, flash, redirect, render_template, request, url_for

from app import kanvas_db
from app.forms.evaluation_instance_forms import EvaluationInstanceForm
from app.models import Evaluation, EvaluationInstance, Section
from app.services.decorators import require_section_open
from app.services.evaluation_instance_service import (
    get_evaluation_instance_with_students_and_grades,
    get_section_id,
)
from app.services.validations import validate_section_for_evaluation

evaluation_instance_bp = Blueprint(
    "evaluation_instance", __name__, url_prefix="/evaluation_instances"
)


@evaluation_instance_bp.route("/")
def index():
    evaluation_instances = EvaluationInstance.query.all()
    return render_template(
        "evaluation_instances/index.html", evaluation_instances=evaluation_instances
    )


@evaluation_instance_bp.route("/<int:id>")
def show(id):
    evaluation_instance, students, student_grades = (
        get_evaluation_instance_with_students_and_grades(id)
    )
    return render_template(
        "evaluation_instances/show.html",
        evaluation_instance=evaluation_instance,
        students=students,
        student_grades=student_grades,
    )


@evaluation_instance_bp.route("/create", methods=["GET", "POST"])
def create():
    form = EvaluationInstanceForm()

    if form.validate_on_submit():
        evaluation = Evaluation.query.get_or_404(form.evaluation_id.data)
        section_id = get_section_id(form.evaluation_id.data)

        validation_error = validate_section_for_evaluation(section_id)
        if validation_error:
            return validation_error

        title = form.title.data
        optional = form.optional.data
        evaluation_id = form.evaluation_id.data

        if EvaluationInstance.query.filter_by(title=title, evaluation_id=evaluation_id).first():
            flash("Instancia de evaluación ya existe.", "danger")
            return render_template("evaluation_instances/create.html", form=form)

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
            return redirect(url_for("evaluation_instance.show", id=evaluation_instance.id))
        except Exception as e:
            kanvas_db.session.rollback()
            flash(f"Error creating evaluation_instance: {e}", "danger")

    return render_template("evaluation_instances/create.html", form=form)


@evaluation_instance_bp.route("/edit/<int:id>", methods=["GET", "POST"])
@require_section_open(lambda id: EvaluationInstance.query.get_or_404(id).evaluation.section)
def edit(id):
    evaluation_instance = EvaluationInstance.query.get_or_404(id)
    form = EvaluationInstanceForm(obj=evaluation_instance)

    if form.validate_on_submit():
        if Evaluation.query.get(form.evaluation_id.data) is None:
            return "Invalid evaluation ID", 400

        title = form.title.data
        optional = form.optional.data
        evaluation_id = form.evaluation_id.data

        existing_evaluation_instance = EvaluationInstance.query.filter_by(
            title=title, evaluation_id=evaluation_id
        ).first()
        if existing_evaluation_instance and existing_evaluation_instance.id != id:
            flash("Instancia de evaluación con ese nombre ya existe.", "danger")
            return render_template(
                "evaluation_instances/create.html",
                form=form,
                evaluation_instance=evaluation_instance,
            )

        evaluation_instance.title = title
        evaluation_instance.optional = optional
        evaluation_instance.evaluation_id = evaluation_id

        try:
            kanvas_db.session.commit()
            return redirect(url_for("evaluation_instance.show", id=evaluation_instance.id))
        except Exception as e:
            kanvas_db.session.rollback()
            flash(f"Error updating evaluation_instance: {e}", "danger")

    return render_template(
        "evaluation_instances/edit.html",
        form=form,
        evaluation_instance=evaluation_instance,
    )


@evaluation_instance_bp.route("/delete/<int:id>")
@require_section_open(lambda id: EvaluationInstance.query.get_or_404(id).evaluation.section)
def delete(id):
    evaluation_instance = EvaluationInstance.query.get_or_404(id)
    try:
        kanvas_db.session.delete(evaluation_instance)
        kanvas_db.session.commit()
    except Exception as e:
        kanvas_db.session.rollback()
        print(f"Error deleting evaluation_instance: {e}")
    return redirect(url_for("evaluation_instance.index"))

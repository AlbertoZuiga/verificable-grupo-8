import math

from flask import Blueprint, flash, redirect, render_template, request, url_for
from sqlalchemy.exc import SQLAlchemyError
from wtforms.validators import AnyOf

from app.extensions import kanvas_db
from app.forms.evaluation_forms import EvaluationForm
from app.models.evaluation import Evaluation
from app.models.section import Section, WeighingType
from app.services.validations import validate_section_for_evaluation
from app.utils.decorators import require_section_open

evaluation_bp = Blueprint("evaluation", __name__, url_prefix="/evaluations")

SHOW_ROUTE = "evaluation.show"
EDIT_INSTANCE_WEIGHTS_ROUTE = "evaluation.edit_instance_weights"


@evaluation_bp.route("/")
def index():
    evaluations = Evaluation.query.all()
    return render_template("evaluations/index.html", evaluations=evaluations)


@evaluation_bp.route("/<int:evaluation_id>")
def show(evaluation_id):
    evaluation = Evaluation.query.get_or_404(evaluation_id)
    return render_template(
        "evaluations/show.html", evaluation=evaluation, WeighingType=WeighingType
    )


@evaluation_bp.route("/<int:evaluation_id>/edit_instance_weights", methods=["GET", "POST"])
def edit_instance_weights(evaluation_id):
    evaluation = Evaluation.query.get_or_404(evaluation_id)

    if request.method == "POST":
        weights = {}
        try:
            for instance in evaluation.instances:
                key = f"instance_{instance.id}"
                weights[instance.id] = float(request.form[key])
        except (ValueError, KeyError) as e:
            flash(f"Entrada inválida para los pesos: {e}", "danger")
            return redirect(url_for(EDIT_INSTANCE_WEIGHTS_ROUTE, evaluation_id=evaluation.id))

        if evaluation.weighing_system == WeighingType.PERCENTAGE:
            total = sum(weights.values())
            if not math.isclose(total, 100.0, rel_tol=1e-9, abs_tol=0.01):
                flash(
                    "La suma de los pesos de las instancias debe ser"
                    " 100 para las evaluaciones ponderadas.",
                    "danger",
                )
                return redirect(url_for(EDIT_INSTANCE_WEIGHTS_ROUTE, evaluation_id=evaluation.id))

        for instance in evaluation.instances:
            instance.instance_weighing = weights[instance.id]

        try:
            kanvas_db.session.commit()
            flash("Pesos de instancias actualizados correctamente", "success")
            return redirect(url_for(SHOW_ROUTE, evaluation_id=evaluation.id))
        except SQLAlchemyError as e:
            flash(f"Error al guardar cambios: {e}", "danger")
            kanvas_db.session.rollback()
            return redirect(url_for(EDIT_INSTANCE_WEIGHTS_ROUTE, evaluation_id=evaluation.id))

    return render_template(
        "evaluations/edit_instance_weights.html",
        evaluation=evaluation,
        WeighingType=WeighingType,
    )


@evaluation_bp.route("/create", methods=["GET", "POST"])
def create():
    form = EvaluationForm()

    choices = [
        (section.id, f"{section.code} - {section.course_instance.course.title}")
        for section in Section.query.all()
    ]
    valid_ids = [section[0] for section in choices]

    form.section_id.choices = choices
    for validator in form.section_id.validators:
        if isinstance(validator, AnyOf):
            validator.values = valid_ids

    if form.validate_on_submit():
        title = form.title.data
        weighing_system = form.weighing_system.data
        section_id = form.section_id.data

        validation_error = validate_section_for_evaluation(section_id)
        if validation_error:
            return redirect(url_for("evaluation.create"))

        if Evaluation.query.filter_by(title=title, section_id=section_id).first():
            flash("Ya existe una evaluación con ese título para la sección.", "danger")
            return render_template("evaluations/create.html", form=form)

        evaluation = Evaluation(
            title=title,
            weighing=0.0,
            weighing_system=weighing_system,
            section_id=section_id,
        )

        try:
            kanvas_db.session.add(evaluation)
            kanvas_db.session.commit()
            return redirect(url_for(SHOW_ROUTE, evaluation_id=evaluation.id))
        except SQLAlchemyError as e:
            kanvas_db.session.rollback()
            flash(f"Error creando evaluation: {e}", "danger")

    return render_template("evaluations/create.html", form=form)


@evaluation_bp.route("/edit/<int:evaluation_id>", methods=["GET", "POST"])
@require_section_open(lambda evaluation_id: Evaluation.query.get_or_404(evaluation_id).section)
def edit(evaluation_id):
    evaluation = Evaluation.query.get_or_404(evaluation_id)
    form = EvaluationForm(obj=evaluation)
    print(evaluation)

    form.section_id.choices = [
        (section.id, f"{section.code} - {section.course_instance.course.title}")
        for section in Section.query.all()
    ]

    if form.validate_on_submit():
        title = form.title.data
        weighing_system = form.weighing_system.data
        section_id = form.section_id.data

        validation_error = validate_section_for_evaluation(section_id)
        if validation_error:
            return validation_error

        existing_evaluation = Evaluation.query.filter_by(title=title, section_id=section_id).first()
        if existing_evaluation and existing_evaluation.id != evaluation_id:
            flash("Ya existe una evaluación con ese título para la seccion.", "danger")
            return render_template("evaluations/edit.html", form=form, evaluation=evaluation)

        evaluation.title = title
        evaluation.weighing = 0.0
        evaluation.weighing_system = weighing_system
        evaluation.section_id = section_id

        try:
            kanvas_db.session.commit()
            return redirect(url_for(SHOW_ROUTE, evaluation_id=evaluation.id))
        except SQLAlchemyError as e:
            kanvas_db.session.rollback()
            flash(f"Error Creating evaluation: {e}", "danger")

    return render_template("evaluations/edit.html", form=form, evaluation=evaluation)


@evaluation_bp.route("/delete/<int:evaluation_id>")
@require_section_open(lambda evaluation_id: Evaluation.query.get_or_404(evaluation_id).section)
def delete(evaluation_id):
    evaluation = Evaluation.query.get_or_404(evaluation_id)
    try:
        kanvas_db.session.delete(evaluation)
        kanvas_db.session.commit()
    except SQLAlchemyError:
        kanvas_db.session.rollback()
        flash(
            "No se puede eliminar.",
            "error",
        )
        return redirect(url_for(SHOW_ROUTE, evaluation_id=id))

    return redirect(url_for("evaluation.index"))

from flask import Blueprint, flash, redirect, render_template, request, url_for
from sqlalchemy.exc import SQLAlchemyError
from wtforms.validators import AnyOf

from app.extensions import kanvas_db
from app.forms.section_forms import SectionForm
from app.models.course_instance import CourseInstance
from app.models.section import Section, WeighingType
from app.models.section_grade import SectionGrade
from app.models.student_evaluation_instance import StudentEvaluationInstance
from app.models.teacher import Teacher
from app.services.section_service import create_section
from app.utils.decorators import require_section_open

MINIMUM_GRADE = 1.0

section_bp = Blueprint("section", __name__, url_prefix="/sections")

INDEX_ROUTE = "section.index"
EDIT_EVALUATION_WEIGHTS_ROUTE = "section.edit_evaluation_weights"


def populate_form_choices(form):
    course_instance_choices = [
        (ci.id, f"{ci.course.title} - {ci.year} (Semestre {ci.semester})")
        for ci in CourseInstance.query.all()
    ]
    form.course_instance_id.choices = course_instance_choices
    for v in form.course_instance_id.validators:
        if isinstance(v, AnyOf):
            v.values = [id for id, _ in course_instance_choices]

    teacher_choices = [
        (t.id, f"{t.user.first_name} {t.user.last_name} ({t.user.email})")
        for t in Teacher.query.all()
    ]
    form.teacher_id.choices = teacher_choices
    for v in form.teacher_id.validators:
        if isinstance(v, AnyOf):
            v.values = [id for id, _ in teacher_choices]


def parse_weights(form_data, section):
    weights = {}
    for key, value in form_data.items():
        if key.startswith("evaluation_"):
            evaluation_id = int(key.split("_")[1])
            if evaluation_id not in [e.id for e in section.evaluations]:
                raise KeyError(f"Evaluación {evaluation_id} no encontrada en la sección.")
            try:
                weights[evaluation_id] = float(value)
            except ValueError as exc:
                raise ValueError(f"Valor inválido para evaluación {key}") from exc
    return weights


@section_bp.route("/")
def index():
    sections = Section.query.all()
    return render_template("sections/index.html", sections=sections)


@section_bp.route("/<int:section_id>")
def show(section_id):
    section = Section.query.get_or_404(section_id)
    return render_template("sections/show.html", section=section, WeighingType=WeighingType)


@section_bp.route("/<int:section_id>/edit_evaluation_weights", methods=["GET", "POST"])
def edit_evaluation_weights(section_id):
    section = Section.query.get_or_404(section_id)

    if request.method == "POST":
        try:
            weights = parse_weights(request.form, section)
        except (ValueError, KeyError) as e:
            flash(f"Entrada inválida para los pesos: {e}", "danger")
            return redirect(url_for(EDIT_EVALUATION_WEIGHTS_ROUTE, section_id=section.id))

        if section.weighing_type == WeighingType.PERCENTAGE:
            total = sum(weights.values())
            if abs(round(total, 2) - 100.0) > 0.01:
                flash(
                    "La suma de los pesos de las evaluaciones"
                    "debe ser 100 para las evaluaciones ponderadas.",
                    "danger",
                )
                return redirect(url_for(EDIT_EVALUATION_WEIGHTS_ROUTE, section_id=section.id))

        for evaluation in section.evaluations:
            evaluation.weighing = weights[evaluation.id]

        try:
            kanvas_db.session.commit()
            flash("Pesos de evaluaciones actualizados correctamente", "success")
            return redirect(url_for("section.show", section_id=section.id))
        except (ValueError, KeyError) as e:
            flash(f"Entrada inválida para los pesos: {e}", "danger")
            return redirect(url_for(EDIT_EVALUATION_WEIGHTS_ROUTE, section_id=section.id))

    return render_template(
        "sections/edit_evaluation_weights.html",
        section=section,
        WeighingType=WeighingType,
    )


@section_bp.route("/create", methods=["GET", "POST"])
def create():
    form = SectionForm()

    populate_form_choices(form)

    if form.validate_on_submit():
        try:
            create_section(
                form.course_instance_id.data,
                form.teacher_id.data,
                form.code.data,
                form.weighing_type.data,
            )
            flash("Sección creada exitosamente", "success")
            return redirect(url_for(INDEX_ROUTE))
        except ValueError as ve:
            flash(str(ve), "warning")
        except SQLAlchemyError as e:
            flash("Error al crear la sección", "danger")
            print(f"Error al crear la sección: {str(e)}")

    return render_template("sections/create.html", form=form)


@section_bp.route("/edit/<int:section_id>", methods=["GET", "POST"])
@require_section_open(lambda section_id: Section.query.get_or_404(section_id))
def edit(section_id):
    section = Section.query.get_or_404(section_id)
    form = SectionForm(obj=section)

    populate_form_choices(form)

    if form.validate_on_submit():
        try:
            section.course_instance_id = form.course_instance_id.data
            section.teacher_id = form.teacher_id.data
            section.code = form.code.data
            section.weighing_type = form.weighing_type.data

            kanvas_db.session.commit()
            print("Sección actualizada exitosamente.")
            return redirect(url_for(INDEX_ROUTE))
        except SQLAlchemyError as e:
            kanvas_db.session.rollback()
            print(f"Error al editar la sección: {str(e)}")

    return render_template("sections/edit.html", section=section, form=form)


@section_bp.route("/delete/<int:section_id>", methods=["POST"])
@require_section_open(lambda section_id: Section.query.get_or_404(section_id))
def delete(section_id):
    section = Section.query.get_or_404(section_id)
    try:
        kanvas_db.session.delete(section)
        kanvas_db.session.commit()
        flash("Sección eliminada con éxito.", "success")
    except SQLAlchemyError as e:
        kanvas_db.session.rollback()
        flash(
            "No se puede eliminar esta sección porque tiene elementos asociados."
            "Elimínalos primero.",
            "danger",
        )
        print(f"Error deleting section: {e}")
        return redirect(url_for("section.show", section_id=id))

    return redirect(url_for(INDEX_ROUTE))


@section_bp.route("/<int:section_id>/close", methods=["POST"])
def close(section_id):
    section = Section.query.get_or_404(section_id)
    students = section.students
    evaluations = section.evaluations

    final_grades = {}

    for student in students:
        total_grade = 0.0
        total_weighing = 0.0
        for evaluation in evaluations:
            evaluation_grade = 0.0
            total_instance_weight = 0.0
            for instance in evaluation.instances:
                student_instance = StudentEvaluationInstance.query.filter_by(
                    student_id=student.id, evaluation_instance_id=instance.id
                ).first()

                if student_instance and student_instance.grade is not None:
                    evaluation_grade += student_instance.grade * instance.instance_weighing
                    total_instance_weight += instance.instance_weighing
                elif not instance.optional:
                    evaluation_grade += MINIMUM_GRADE * instance.instance_weighing
                    total_instance_weight += instance.instance_weighing

            if total_instance_weight > 0:
                evaluation_grade /= total_instance_weight
                total_grade += evaluation_grade * evaluation.weighing
                total_weighing += evaluation.weighing

        total_grade /= total_weighing
        grade = SectionGrade(student_id=student.id, section_id=section_id, grade=total_grade)
        kanvas_db.session.add(grade)
        final_grades[student.id] = total_grade

    section.closed = True
    kanvas_db.session.commit()

    flash("La sección fue cerrada exitosamente.", "success")
    return redirect(url_for("section.grades", section_id=section_id))


@section_bp.route("/<int:section_id>/grades", methods=["GET"])
def grades(section_id):
    section = Section.query.get_or_404(section_id)
    return render_template(
        "sections/grades.html",
        section=section,
        StudentEvaluationInstance=StudentEvaluationInstance,
        SectionGrade=SectionGrade,
    )

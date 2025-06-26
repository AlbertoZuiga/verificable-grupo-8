from flask import Blueprint, flash, redirect, render_template, request, url_for

from app import kanvas_db
from app.forms.section_forms import SectionForm
from app.models import (CourseInstance, Section, SectionGrade,
                        StudentEvaluationInstance, Teacher, WeighingType)
from app.services.decorators import require_section_open
from app.services.section_service import create_section

MINIMUM_GRADE = 1.0

section_bp = Blueprint("section", __name__, url_prefix="/sections")


@section_bp.route("/")
def index():
    sections = Section.query.all()
    return render_template("sections/index.html", sections=sections)


@section_bp.route("/<int:id>")
def show(id):
    section = Section.query.get_or_404(id)
    return render_template("sections/show.html", section=section, WeighingType=WeighingType)


@section_bp.route("/<int:id>/edit_evaluation_weights", methods=["GET", "POST"])
def edit_evaluation_weights(id):
    section = Section.query.get_or_404(id)

    if request.method == "POST":
        weights = {}
        try:
            for evaluation in section.evaluations:
                key = f"evaluation_{evaluation.id}"
                weights[evaluation.id] = float(request.form[key])
        except (ValueError, KeyError) as e:
            flash(f"Entrada inválida para los pesos: {e}", "danger")
            return redirect(url_for("section.edit_evaluation_weights", id=section.id))

        # Validación para evaluaciones con porcentajes
        if section.weighing_type == WeighingType.PERCENTAGE:
            total = sum(weights.values())
            if round(total, 2) != 100.0:
                flash(
                    "La suma de los pesos de las evaluaciones\
                    debe ser 100 para las evaluaciones ponderadas.",
                    "danger",
                )
                return redirect(url_for("section.edit_evaluation_weights", id=section.id))

        # Asignar pesos nuevos
        for evaluation in section.evaluations:
            evaluation.weighing = weights[evaluation.id]

        try:
            kanvas_db.session.commit()
            flash("Pesos de evaluaciones actualizados correctamente", "success")
            return redirect(url_for("section.show", id=section.id))
        except Exception as e:
            kanvas_db.session.rollback()
            flash(f"Error al guardar cambios: {e}", "danger")

    return render_template(
        "sections/edit_evaluation_weights.html",
        section=section,
        WeighingType=WeighingType,
    )


@section_bp.route("/create", methods=["GET", "POST"])
def create():
    form = SectionForm()

    form.course_instance_id.choices = [
        (ci.id, f"{ci.course.title} - {ci.year} (Semestre {ci.semester})")
        for ci in CourseInstance.query.all()
    ]
    form.teacher_id.choices = [
        (t.id, f"{t.user.first_name} {t.user.last_name} ({t.user.email})")
        for t in Teacher.query.all()
    ]
    form.weighing_type.choices = [(wt.name, wt.value) for wt in WeighingType]

    if form.validate_on_submit():
        try:
            create_section(
                form.course_instance_id.data,
                form.teacher_id.data,
                form.code.data,
                form.weighing_type.data,
            )
            flash("Sección creada exitosamente", "success")
            return redirect(url_for("section.index"))
        except ValueError as ve:
            flash(str(ve), "warning")
        except Exception as e:
            flash("Error al crear la sección", "danger")
            print(f"Error al crear la sección: {str(e)}")

    return render_template("sections/create.html", form=form)


@section_bp.route("/edit/<int:id>", methods=["GET", "POST"])
@require_section_open(Section.query.get_or_404(id))
def edit(id):
    section = Section.query.get_or_404(id)
    form = SectionForm(obj=section)

    form.course_instance_id.choices = [
        (ci.id, f"{ci.course.title} - {ci.year} (Semestre {ci.semester})")
        for ci in CourseInstance.query.all()
    ]
    form.teacher_id.choices = [
        (t.id, f"{t.user.first_name} {t.user.last_name} ({t.user.email})")
        for t in Teacher.query.all()
    ]
    form.weighing_type.choices = [(wt.name, wt.value) for wt in WeighingType]

    if form.validate_on_submit():
        try:
            section.course_instance_id = form.course_instance_id.data
            section.teacher_id = form.teacher_id.data
            section.code = form.code.data
            section.weighing_type = form.weighing_type.data

            kanvas_db.session.commit()
            print("Sección actualizada exitosamente.")
            return redirect(url_for("section.index"))
        except Exception as e:
            kanvas_db.session.rollback()
            print(f"Error al editar la sección: {str(e)}")

    return render_template("sections/edit.html", section=section, form=form)


@section_bp.route("/delete/<int:id>", methods=["POST"])
@require_section_open(Section.query.get_or_404(id))
def delete(id):
    section = Section.query.get_or_404(id)
    try:
        kanvas_db.session.delete(section)
        kanvas_db.session.commit()
        flash("Sección eliminada con éxito.", "success")
    except Exception as e:
        kanvas_db.session.rollback()
        flash(
            "No se puede eliminar esta sección porque tiene elementos asociados.\
            Elimínalos primero.",
            "danger",
        )
        print(f"Error deleting section: {e}")
        return redirect(url_for("section.show", id=id))

    return redirect(url_for("section.index"))


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

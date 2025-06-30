import json
from json import JSONDecodeError

from flask import Blueprint, flash, redirect, render_template, request, url_for
from sqlalchemy.exc import SQLAlchemyError

from app.models.section import Section
from app.models.student_section import StudentSection
from app.services.student_section_service import (
    add_student_to_section,
    get_students_not_in_section,
    remove_student_from_section,
)

student_section_bp = Blueprint(
    "student_section", __name__, url_prefix="/sections/<int:section_id>/students/"
)

INDEX_ROUTE = "student_section.index"


@student_section_bp.route("/")
def index(section_id):
    section = Section.query.get_or_404(section_id)
    student_sections = StudentSection.query.filter_by(section_id=section_id).all()
    return render_template(
        "student_sections/index.html",
        section=section,
        student_sections=student_sections,
    )


@student_section_bp.route("/add", methods=["GET", "POST"])
def add_user(section_id):
    section = Section.query.get(section_id)
    if section is None:
        flash("La sección no existe.", "danger")
        return redirect(url_for("section.index"))
    students = get_students_not_in_section(section_id)

    if section.closed:
        flash("Esta sección está cerrada y no puede ser modificada.", "warning")
        return redirect(url_for("section.show", section_id=section.id))

    if request.method == "POST":
        return handle_add_user_post(section_id)

    context = {"section": section, "students": students}
    return render_template("student_sections/add.html", **context)


def handle_add_user_post(section_id):
    ids_json = request.form.get("student_ids")

    if not ids_json:
        flash("Debes agregar al menos un estudiante.", "danger")
        return redirect(url_for(INDEX_ROUTE, section_id=section_id))

    try:
        student_ids = json.loads(ids_json)
        added = sum(
            1 for student_id in student_ids if add_student_to_section(student_id, section_id)
        )

        if added:
            flash(f"{added} estudiante(s) agregados exitosamente.", "success")
        else:
            flash("Los estudiantes ya estaban en esta sección.", "warning")
    except (JSONDecodeError, SQLAlchemyError):
        flash("Error al procesar los estudiantes.", "danger")

    return redirect(url_for(INDEX_ROUTE, section_id=section_id))


@student_section_bp.route("/remove/<int:student_id>", methods=["POST"])
def remove_user(section_id, student_id):
    section = Section.query.get_or_404(section_id)

    if section.closed:
        flash("Esta sección está cerrada y no puede ser modificada.", "warning")
        return redirect(url_for("section.show", section_id=section.id))
    if remove_student_from_section(section_id, student_id):
        flash("Usuario removido de la sección.", "success")
    else:
        flash("Error al remover usuario de la sección.", "danger")
    return redirect(url_for(INDEX_ROUTE, section_id=section_id))

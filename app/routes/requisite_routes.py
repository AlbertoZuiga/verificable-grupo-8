from flask import Blueprint, flash, redirect, request, url_for
from sqlalchemy.exc import SQLAlchemyError

from app import kanvas_db
from app.models.course import Course
from app.models.requisite import Requisite

requisite_bp = Blueprint("requisite", __name__, url_prefix="/requisites")


@requisite_bp.route("/create", methods=["POST"])
def create():
    course_id = request.form.get("course_id")
    requisite_id = request.form.get("requisite_id")

    if not course_id or not requisite_id:
        flash("Debe seleccionar un curso y su requisito.", "danger")
        return redirect(url_for("course.show", id=course_id))

    if Requisite.query.filter_by(course_id=requisite_id, course_requisite_id=course_id).first():
        flash(
            "No se puede asignar como requisito un curso que depende del curso actual.",
            "danger",
        )
        return redirect(url_for("course.show", id=course_id))

    course = Course.query.get_or_404(course_id)
    new_requisite = Course.query.get_or_404(requisite_id)

    if course.has_cyclic_requisite(new_requisite):
        flash(
            "No se puede asignar como requisito un curso que depende del curso actual.",
            "danger",
        )
        return redirect(url_for("course.show", id=course_id))

    new_requisite = Requisite(course_id=course_id, course_requisite_id=requisite_id)

    try:
        kanvas_db.session.add(new_requisite)
        kanvas_db.session.commit()
        print("Requisito añadido con éxito.")
    except SQLAlchemyError as e:
        kanvas_db.session.rollback()
        print(f"Error al crear el requisito: {e}")

    return redirect(url_for("course.show", id=course_id))


@requisite_bp.route("/delete/<int:requisite_id>")
def delete(requisite_id):
    requisite = Requisite.query.get_or_404(requisite_id)
    course_id = requisite.course_id

    try:
        kanvas_db.session.delete(requisite)
        kanvas_db.session.commit()
        print("Requisito eliminado con éxito.")
    except SQLAlchemyError as e:
        kanvas_db.session.rollback()
        print(f"Error al eliminar el requisito: {e}")

    return redirect(url_for("course.show", id=course_id))

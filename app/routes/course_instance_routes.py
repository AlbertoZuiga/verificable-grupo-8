from flask import Blueprint, flash, redirect, render_template, url_for
from sqlalchemy.exc import SQLAlchemyError

from app.extensions import kanvas_db
from app.forms.course_instance_forms import CourseInstanceForm
from app.models.course import Course
from app.models.course_instance import CourseInstance, Semester

course_instance_bp = Blueprint("course_instance", __name__, url_prefix="/course_instances")


@course_instance_bp.route("/")
def index():
    course_instances = CourseInstance.query.all()
    return render_template("course_instances/index.html", course_instances=course_instances)


@course_instance_bp.route("/<int:course_instance_id>")
def show(course_instance_id):
    course_instance = CourseInstance.query.get_or_404(course_instance_id)
    return render_template("course_instances/show.html", course_instance=course_instance)


@course_instance_bp.route("/create", methods=["GET", "POST"])
def create():
    courses = Course.query.all()
    form = CourseInstanceForm()
    form.course_id.choices = [(course.id, course.title) for course in courses]

    if form.validate_on_submit():
        course_id = form.course_id.data
        year = form.year.data
        semester = form.semester.data

        if CourseInstance.query.filter_by(
            course_id=course_id, year=year, semester=semester
        ).first():
            flash("Ya existe la instancia de curso.", "danger")
            return render_template("course_instances/create.html", form=form, courses=courses)

        new_course_instance = CourseInstance(
            course_id=course_id, year=year, semester=Semester[semester]
        )
        kanvas_db.session.add(new_course_instance)
        kanvas_db.session.commit()
        flash("Instancia del curso creada exitosamente.", "success")
        return redirect(url_for("course_instance.show", id=new_course_instance.id))

    return render_template("course_instances/create.html", form=form, courses=courses)


@course_instance_bp.route("/edit/<int:course_instance_id>", methods=["GET", "POST"])
def edit(course_instance_id):
    course_instance = CourseInstance.query.get_or_404(course_instance_id)
    courses = Course.query.all()
    form = CourseInstanceForm(obj=course_instance)
    form.course_id.choices = [(course.id, course.title) for course in courses]

    if form.validate_on_submit():
        course_instance.course_id = form.course_id.data
        course_instance.year = form.year.data
        course_instance.semester = Semester[form.semester.data]

        kanvas_db.session.commit()
        flash("Instancia del curso actualizada exitosamente.", "success")
        return redirect(url_for("course_instance.show", id=course_instance.id))

    return render_template("course_instances/create.html", form=form, courses=courses)


@course_instance_bp.route("/delete/<int:course_instance_id>", methods=["POST"])
def delete(course_instance_id):
    course_instance = CourseInstance.query.get_or_404(course_instance_id)
    try:
        kanvas_db.session.delete(course_instance)
        kanvas_db.session.commit()
        flash("Instancia del curso eliminada con éxito.", "success")
    except SQLAlchemyError as e:
        kanvas_db.session.rollback()
        flash(f"Error deleting course_instance: {e}", "danger")
        return redirect(url_for("course_instance.show", id=course_instance_id))

    return redirect(url_for("course_instance.index"))

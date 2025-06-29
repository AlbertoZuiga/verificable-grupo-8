from flask import Blueprint, flash, redirect, render_template, url_for
from sqlalchemy.exc import SQLAlchemyError

from app.extensions import kanvas_db
from app.forms.course_forms import CourseForm
from app.models.course import Course
from app.services.course_service import get_course_and_other_courses

course_bp = Blueprint("course", __name__, url_prefix="/courses")

CREATE_HTML = "courses/create.html"
EDIT_HTML = "courses/edit.html"


@course_bp.route("/")
def index():
    courses = Course.query.all()
    return render_template("courses/index.html", courses=courses)


@course_bp.route("/<int:course_id>")
def show(course_id):
    course, courses = get_course_and_other_courses(course_id)
    return render_template("courses/show.html", course=course, courses=courses)


@course_bp.route("/create", methods=["GET", "POST"])
def create():
    form = CourseForm()
    if form.validate_on_submit():
        title = form.title.data
        code = form.code.data
        course_credits = form.credits.data

        if Course.query.filter_by(title=title).first():
            flash("Ya existe un curso con ese título.", "danger")
            return render_template(CREATE_HTML, form=form)

        if Course.query.filter_by(code=code).first():
            flash("Ya existe un curso con ese codigo.", "danger")
            return render_template(CREATE_HTML, form=form)

        new_course = Course(title=title, code=code, credits=course_credits)
        kanvas_db.session.add(new_course)
        kanvas_db.session.commit()
        flash("Instancia del curso creada exitosamente.", "success")
        return redirect(url_for("course.show", course_id=new_course.id))

    return render_template(CREATE_HTML, form=form)


@course_bp.route("/edit/<int:course_id>", methods=["GET", "POST"])
def edit(course_id):
    course = Course.query.get_or_404(course_id)
    form = CourseForm(obj=course)
    if form.validate_on_submit():
        title = form.title.data
        code = form.code.data
        course_credits = form.credits.data

        existing_course = Course.query.filter_by(title=title).first()
        if existing_course and existing_course.id != course_id:
            flash("Ya existe un curso con ese título.", "danger")
            return render_template(EDIT_HTML, form=form, course=course)

        existing_course = Course.query.filter_by(code=code).first()
        if existing_course and existing_course.id != course_id:
            flash("Ya existe un curso con ese codigo.", "danger")
            return render_template(EDIT_HTML, form=form, course=course)

        course.title = title
        course.code = code
        course.credits = course_credits

        kanvas_db.session.commit()
        flash("Instancia del curso actualizada exitosamente.", "success")
        return redirect(url_for("course.show", course_id=course.id))

    return render_template(EDIT_HTML, form=form, course=course)


@course_bp.route("/delete/<int:course_id>")
def delete(course_id):
    course = Course.query.get_or_404(course_id)
    try:
        kanvas_db.session.delete(course)
        kanvas_db.session.commit()
    except SQLAlchemyError as e:
        kanvas_db.session.rollback()
        print(f"Error deleting course: {e}")
    return redirect(url_for("course.index"))

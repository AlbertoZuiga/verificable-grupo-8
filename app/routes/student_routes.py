from flask import Blueprint, flash, redirect, render_template, url_for
from wtforms.validators import NoneOf

from app.extensions import kanvas_db
from app.forms.student_forms import CreateStudentForm, EditStudentForm
from app.models.student import Student
from app.models.user import User
from app.services.user_service import create_user_from_form

student_bp = Blueprint("student", __name__, url_prefix="/students")

INDEX_ROUTE = "student.index"


def populate_form_choices(form, original_email=None):
    existing_emails = [user.email for user in User.query.all() if user.email != original_email]
    for v in form.email.validators:
        if isinstance(v, NoneOf):
            v.values = existing_emails


@student_bp.route("/")
def index():
    students = Student.query.all()
    return render_template("students/index.html", students=students)


@student_bp.route("/<int:student_id>")
def show(student_id):
    student = Student.query.get_or_404(student_id)
    return render_template("students/show.html", student=student)


@student_bp.route("/create", methods=["GET", "POST"])
def create():
    form = CreateStudentForm()
    populate_form_choices(form)

    if form.validate_on_submit():
        new_user = create_user_from_form(form=form)

        new_student = Student(
            user_id=new_user.id, university_entry_year=form.university_entry_year.data
        )
        kanvas_db.session.add(new_student)
        kanvas_db.session.commit()
        flash("Estudiante creado correctamente", "success")
        return redirect(url_for("student.show", student_id=new_student.id))
    return render_template("students/create.html", form=form)


@student_bp.route("/edit/<int:student_id>", methods=["GET", "POST"])
def edit(student_id):
    student = Student.query.get_or_404(student_id)
    user = student.user

    form = EditStudentForm(
        original_email=user.email,
        university_entry_year=student.university_entry_year,
        obj=user,
    )
    populate_form_choices(form, original_email=user.email)

    if form.validate_on_submit():
        user.first_name = form.first_name.data
        user.last_name = form.last_name.data
        user.email = form.email.data
        student.university_entry_year = form.university_entry_year.data

        kanvas_db.session.commit()
        flash("Estudiante actualizado correctamente.")
        return redirect(url_for("student.show", student_id=student_id))

    return render_template("students/edit.html", form=form, student=student)


@student_bp.route("/delete/<int:student_id>")
def delete(student_id):
    student = Student.query.get_or_404(student_id)

    kanvas_db.session.delete(student)
    kanvas_db.session.commit()
    return redirect(url_for(INDEX_ROUTE))

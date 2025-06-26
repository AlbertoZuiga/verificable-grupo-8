from flask import Blueprint, redirect, render_template, url_for

from app import kanvas_db
from app.forms.student_forms import StudentCreateForm, StudentEditForm
from app.models import Student, User

student_bp = Blueprint("student", __name__, url_prefix="/students")


@student_bp.route("/")
def index():
    students = Student.query.all()
    return render_template("students/index.html", students=students)


@student_bp.route("/<int:id>")
def show(id):
    student = Student.query.get_or_404(id)
    return render_template("students/show.html", student=student)


@student_bp.route("/create", methods=["GET", "POST"])
def create():
    form = StudentCreateForm()
    if form.validate_on_submit():
        new_user = User(
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            email=form.email.data,
        )
        new_user.set_password(form.password.data)
        kanvas_db.session.add(new_user)
        kanvas_db.session.flush()

        new_student = Student(
            user_id=new_user.id, university_entry_year=form.university_entry_year.data
        )
        kanvas_db.session.add(new_student)
        kanvas_db.session.commit()
        return redirect(url_for("student.index"))
    return render_template("students/create.html", form=form)


@student_bp.route("/edit/<int:id>", methods=["GET", "POST"])
def edit(id):
    student = Student.query.get_or_404(id)
    user = student.user

    form = StudentEditForm(original_email=user.email, obj=user)

    if form.validate_on_submit():
        user.first_name = form.first_name.data
        user.last_name = form.last_name.data
        user.email = form.email.data
        student.university_entry_year = form.university_entry_year.data

        kanvas_db.session.commit()
        return redirect(url_for("student.index"))

    return render_template("students/edit.html", form=form, student=student)


@student_bp.route("/delete/<int:id>")
def delete(id):
    student = Student.query.get_or_404(id)

    kanvas_db.session.delete(student)
    kanvas_db.session.commit()
    return redirect(url_for("student.index"))

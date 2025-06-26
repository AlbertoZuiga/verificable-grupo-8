from flask import Blueprint, redirect, render_template, url_for

from app import kanvas_db
from app.forms.teacher_forms import TeacherCreateForm, TeacherEditForm
from app.models import Teacher, User

teacher_bp = Blueprint("teacher", __name__, url_prefix="/teachers")


@teacher_bp.route("/")
def index():
    teachers = Teacher.query.all()
    return render_template("teachers/index.html", teachers=teachers)


@teacher_bp.route("/<int:id>")
def show(id):
    teacher = Teacher.query.get_or_404(id)
    return render_template("teachers/show.html", teacher=teacher)


@teacher_bp.route("/create", methods=["GET", "POST"])
def create():
    form = TeacherCreateForm()
    if form.validate_on_submit():
        new_user = User(
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            email=form.email.data,
        )
        new_user.set_password(form.password.data)
        kanvas_db.session.add(new_user)
        kanvas_db.session.flush()

        new_teacher = Teacher(user_id=new_user.id)
        kanvas_db.session.add(new_teacher)
        kanvas_db.session.commit()
        return redirect(url_for("teacher.index"))
    return render_template("teachers/create.html", form=form)


@teacher_bp.route("/edit/<int:id>", methods=["GET", "POST"])
def edit(id):
    teacher = Teacher.query.get_or_404(id)
    user = teacher.user
    form = TeacherEditForm(original_email=user.email, obj=user)
    if form.validate_on_submit():
        user.first_name = form.first_name.data
        user.last_name = form.last_name.data
        user.email = form.email.data
        kanvas_db.session.commit()
        return redirect(url_for("teacher.index"))
    return render_template("teachers/edit.html", form=form, teacher=teacher)


@teacher_bp.route("/delete/<int:id>")
def delete(id):
    teacher = Teacher.query.get_or_404(id)

    kanvas_db.session.delete(teacher)
    kanvas_db.session.commit()
    return redirect(url_for("teacher.index"))

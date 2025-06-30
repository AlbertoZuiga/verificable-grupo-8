from flask import Blueprint, flash, redirect, render_template, url_for
from wtforms.validators import NoneOf

from app.extensions import kanvas_db
from app.forms.teacher_forms import CreateTeacherForm, EditTeacherForm
from app.models.teacher import Teacher
from app.models.user import User
from app.services.user_service import create_user_from_form

teacher_bp = Blueprint("teacher", __name__, url_prefix="/teachers")

INDEX_ROUTE = "teacher.index"


def populate_form_choices(form, original_email=None):
    existing_emails = [user.email for user in User.query.all() if user.email != original_email]
    for v in form.email.validators:
        if isinstance(v, NoneOf):
            v.values = existing_emails


@teacher_bp.route("/")
def index():
    teachers = Teacher.query.all()
    return render_template("teachers/index.html", teachers=teachers)


@teacher_bp.route("/<int:teacher_id>")
def show(teacher_id):
    teacher = Teacher.query.get_or_404(teacher_id)
    return render_template("teachers/show.html", teacher=teacher)


@teacher_bp.route("/create", methods=["GET", "POST"])
def create():
    form = CreateTeacherForm()
    populate_form_choices(form)

    if form.validate_on_submit():
        new_user = create_user_from_form(form=form)

        new_teacher = Teacher(user_id=new_user.id)
        kanvas_db.session.add(new_teacher)
        kanvas_db.session.commit()
        flash("Profesor creado correctamente.", "success")
        return redirect(url_for("teacher.show", teacher_id=new_teacher.id))
    return render_template("teachers/create.html", form=form)


@teacher_bp.route("/edit/<int:teacher_id>", methods=["GET", "POST"])
def edit(teacher_id):
    teacher = Teacher.query.get_or_404(teacher_id)
    user = teacher.user

    form = EditTeacherForm(original_email=user.email, obj=user)
    populate_form_choices(form, original_email=user.email)

    if form.validate_on_submit():
        user.first_name = form.first_name.data
        user.last_name = form.last_name.data
        user.email = form.email.data

        kanvas_db.session.commit()
        flash("Profesor actualizado correctamente.", "success")
        return redirect(url_for("teacher.show", teacher_id=teacher.id))

    return render_template("teachers/edit.html", form=form, teacher=teacher)


@teacher_bp.route("/delete/<int:teacher_id>")
def delete(teacher_id):
    teacher = Teacher.query.get_or_404(teacher_id)

    kanvas_db.session.delete(teacher)
    kanvas_db.session.commit()
    return redirect(url_for(INDEX_ROUTE))

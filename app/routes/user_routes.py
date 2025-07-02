from flask import Blueprint, flash, redirect, render_template, url_for
from wtforms.validators import NoneOf

from app.extensions import kanvas_db
from app.forms.user_forms import CreateUserForm, EditUserForm
from app.models.user import User
from app.services.user_service import create_user_from_form

user_bp = Blueprint("user", __name__, url_prefix="/users")

INDEX_ROUTE = "user.index"


def populate_form_choices(form, original_email=None):
    existing_emails = [user.email for user in User.query.all() if user.email != original_email]
    for v in form.email.validators:
        if isinstance(v, NoneOf):
            v.values = existing_emails


@user_bp.route("/")
def index():
    users = User.query.all()
    return render_template("users/index.html", users=users)


@user_bp.route("/<int:user_id>")
def show(user_id):
    user = User.query.get_or_404(user_id)
    return render_template("users/show.html", user=user)


@user_bp.route("/create", methods=["GET", "POST"])
def create():
    form = CreateUserForm()
    populate_form_choices(form)

    if form.validate_on_submit():
        new_user = create_user_from_form(form=form)

        flash("Usuario creado correctamente.", "success")
        return redirect(url_for("user.show", user_id=new_user.id))
    return render_template("users/create.html", form=form)


@user_bp.route("/edit/<int:user_id>", methods=["GET", "POST"])
def edit(user_id):
    user = User.query.get_or_404(user_id)
    form = EditUserForm(obj=user)
    populate_form_choices(form)

    if form.validate_on_submit():
        user.first_name = form.first_name.data
        user.last_name = form.last_name.data
        user.email = form.email.data

        kanvas_db.session.commit()
        flash("Usuario actualizado correctamente.", "success")
        return redirect(url_for("user.show", user_id=user.id))

    return render_template("users/edit.html", form=form, user=user)


@user_bp.route("/delete/<int:user_id>")
def delete(user_id):
    user = User.query.get_or_404(user_id)
    kanvas_db.session.delete(user)
    kanvas_db.session.commit()
    return redirect(url_for(INDEX_ROUTE))

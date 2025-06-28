from flask import Blueprint, flash, redirect, render_template, url_for

from app.extensions import kanvas_db
from app.forms.user_forms import EditUserForm, UserForm
from app.models.user import User

user_bp = Blueprint("user", __name__, url_prefix="/users")


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
    form = UserForm()
    if form.validate_on_submit():
        email = form.email.data

        if User.query.filter_by(email=email).first():
            flash("Ya existe un usuario con ese correo.", "danger")
            return render_template("users/create.html", form=form)

        new_user = User(first_name=form.first_name.data, last_name=form.last_name.data, email=email)
        new_user.set_password(form.password.data)
        kanvas_db.session.add(new_user)
        kanvas_db.session.commit()
        return redirect(url_for("user.index"))
    return render_template("users/create.html", form=form)


@user_bp.route("/edit/<int:user_id>", methods=["GET", "POST"])
def edit(user_id):
    user = User.query.get_or_404(user_id)
    form = EditUserForm(obj=user)

    if form.validate_on_submit():
        email = form.email.data
        existing_user = User.query.filter_by(email=email).first()
        if existing_user and existing_user.id != user_id:
            flash("Ya existe un usuario con ese correo.", "danger")
            return render_template("users/edit.html", form=form, user=user)

        form.populate_obj(user)
        kanvas_db.session.commit()
        return redirect(url_for("user.index"))

    return render_template("users/edit.html", form=form, user=user)


@user_bp.route("/delete/<int:user_id>")
def delete(user_id):
    user = User.query.get_or_404(user_id)
    kanvas_db.session.delete(user)
    kanvas_db.session.commit()
    return redirect(url_for("user.index"))

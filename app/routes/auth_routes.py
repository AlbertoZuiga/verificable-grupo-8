from flask import Blueprint, flash, redirect, render_template, url_for
from flask_login import login_required, login_user, logout_user

from app.forms.auth_forms import LoginForm
from app.models.user import User

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            login_user(user)
            flash("Sesión iniciada", "success")
            return redirect(url_for("main.index"))
        flash("Usuario o contraseña inválidos", "danger")
    return render_template("auth/login.html", form=form)


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Sesión cerrada", "success")
    return redirect(url_for("auth.login"))

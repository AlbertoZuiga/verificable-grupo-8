from flask import Blueprint, request, render_template, redirect, url_for, flash

from app import kanvas_db
from app.models.classroom import Classroom
from app.forms.classroom_forms import ClassroomForm

classroom_bp = Blueprint("classroom", __name__, url_prefix="/classrooms")


@classroom_bp.route("/", methods=["GET"])
def index():
    classrooms = Classroom.query.all()
    return render_template("classrooms/index.html", classrooms=classrooms)


@classroom_bp.route("/<int:id>", methods=["GET"])
def show(id):
    classroom = Classroom.query.get_or_404(id)
    return render_template("classrooms/show.html", classroom=classroom)


@classroom_bp.route("/create", methods=["GET", "POST"])
def create():
    form = ClassroomForm()

    if form.validate_on_submit():
        name = (form.name.data,)
        capacity = form.capacity.data

        if Classroom.query.filter_by(name=name).first():
            flash("Ya existe una sala con ese nombre.", "danger")
            return render_template("classrooms/create.html", form=form)

        new_classroom = Classroom(name=name, capacity=capacity)
        kanvas_db.session.add(new_classroom)
        kanvas_db.session.commit()
        flash("Sala creada exitosamente", "success")
        return redirect(url_for("classroom.show", id=new_classroom.id))

    return render_template("classrooms/create.html", form=form)


@classroom_bp.route("/<int:id>/edit", methods=["GET", "POST"])
def edit(id):
    classroom = Classroom.query.get_or_404(id)
    form = ClassroomForm(obj=classroom)

    if form.validate_on_submit():
        classroom.name = (form.name.data,)
        classroom.capacity = form.capacity.data

        kanvas_db.session.commit()
        flash("Sala actualizada exitosamente", "success")
        return redirect(url_for("classroom.show", id=classroom.id))

    return render_template("classrooms/create.html", form=form)


@classroom_bp.route("/<int:id>/delete", methods=["POST"])
def delete(id):
    classroom = Classroom.query.get_or_404(id)
    kanvas_db.session.delete(classroom)
    kanvas_db.session.commit()
    flash("Sala eliminada exitosamente", "success")
    return redirect(url_for("classroom.index"))

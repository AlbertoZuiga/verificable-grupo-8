from flask import Blueprint, flash, redirect, render_template, url_for

from app.extensions import kanvas_db
from app.forms.classroom_forms import ClassroomForm
from app.models.classroom import Classroom

classroom_bp = Blueprint("classroom", __name__, url_prefix="/classrooms")

CREATE_HTML = "classrooms/create.html"


@classroom_bp.route("/", methods=["GET"])
def index():
    classrooms = Classroom.query.all()
    return render_template("classrooms/index.html", classrooms=classrooms)


@classroom_bp.route("/<int:classroom_id>", methods=["GET"])
def show(classroom_id):
    classroom = Classroom.query.get_or_404(classroom_id)
    return render_template("classrooms/show.html", classroom=classroom)


@classroom_bp.route("/create", methods=["GET", "POST"])
def create():
    form = ClassroomForm()

    if form.validate_on_submit():
        name = (form.name.data,)
        capacity = form.capacity.data

        if Classroom.query.filter_by(name=name).first():
            flash("Ya existe una sala con ese nombre.", "danger")
            return render_template(CREATE_HTML, form=form)

        new_classroom = Classroom(name=name, capacity=capacity)
        kanvas_db.session.add(new_classroom)
        kanvas_db.session.commit()
        flash("Sala creada exitosamente", "success")
        return redirect(url_for("classroom.show", id=new_classroom.id))

    return render_template(CREATE_HTML, form=form)


@classroom_bp.route("/<int:classroom_id>/edit", methods=["GET", "POST"])
def edit(classroom_id):
    classroom = Classroom.query.get_or_404(classroom_id)
    form = ClassroomForm(obj=classroom)

    if form.validate_on_submit():
        classroom.name = (form.name.data,)
        classroom.capacity = form.capacity.data

        kanvas_db.session.commit()
        flash("Sala actualizada exitosamente", "success")
        return redirect(url_for("classroom.show", id=classroom.id))

    return render_template(CREATE_HTML, form=form)


@classroom_bp.route("/<int:classroom_id>/delete", methods=["POST"])
def delete(classroom_id):
    classroom = Classroom.query.get_or_404(classroom_id)
    kanvas_db.session.delete(classroom)
    kanvas_db.session.commit()
    flash("Sala eliminada exitosamente", "success")
    return redirect(url_for("classroom.index"))

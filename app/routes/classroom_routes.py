from flask import Blueprint, request, render_template, redirect, url_for, flash
from app.models.classroom import Classroom
from app import kanvas_db

classroom_bp = Blueprint('classroom', __name__)

@classroom_bp.route('/classrooms/create', methods=['GET'])
def create_form():
    return render_template('classrooms/create.html')

@classroom_bp.route('/classrooms/create', methods=['POST'])
def create():
    name = request.form['name']
    capacity = request.form['capacity']
    new_classroom = Classroom(name=name, capacity=capacity)
    kanvas_db.session.add(new_classroom)
    kanvas_db.session.commit()
    flash('Sala creada exitosamente', 'success')
    return redirect(url_for('classroom.index'))

@classroom_bp.route('/classrooms', methods=['GET'])
def index():
    classrooms = Classroom.query.all()
    return render_template('classrooms/index.html', classrooms=classrooms)

@classroom_bp.route('/classrooms/<int:id>', methods=['GET'])
def show(id):
    classroom = Classroom.query.get_or_404(id)
    return render_template('classrooms/show.html', classroom=classroom)

@classroom_bp.route('/classrooms/<int:id>/edit', methods=['GET'])
def edit_form(id):
    classroom = Classroom.query.get_or_404(id)
    return render_template('classrooms/edit.html', classroom=classroom)

@classroom_bp.route('/classrooms/<int:id>/edit', methods=['POST'])
def edit(id):
    classroom = Classroom.query.get_or_404(id)
    classroom.name = request.form['name']
    classroom.capacity = request.form['capacity']
    kanvas_db.session.commit()
    flash('Sala actualizada exitosamente', 'info')
    return redirect(url_for('classroom.index'))

@classroom_bp.route('/classrooms/<int:id>/delete', methods=['POST'])
def delete(id):
    classroom = Classroom.query.get_or_404(id)
    kanvas_db.session.delete(classroom)
    kanvas_db.session.commit()
    flash('Sala eliminada exitosamente', 'success')
    return redirect(url_for('classroom.index'))

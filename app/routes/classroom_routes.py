from flask import Blueprint, request, jsonify, render_template, redirect, url_for
from app.models.classroom import Classroom
from app import kanvas_db

classroom_bp = Blueprint('classroom', __name__)

@classroom_bp.route('/classrooms', methods=['POST'])
def create():
    data = request.get_json()
    new_classroom = Classroom(name=data['name'], capacity=data['capacity'])
    kanvas_db.session.add(new_classroom)
    kanvas_db.session.commit()
    return render_template('classrooms/create.html')

@classroom_bp.route('/classrooms', methods=['GET'])
def index():
    classrooms = Classroom.query.all()
    return render_template('classrooms/index.html', classrooms=classrooms)

@classroom_bp.route('/classrooms/<int:id>', methods=['GET'])
def show(id):
    classroom = Classroom.query.get_or_404(id)
    return render_template('classrooms/show.html', classroom=classroom)

@classroom_bp.route('/classrooms/<int:id>', methods=['PUT'])
def edit(id):
    data = request.get_json()
    classroom = Classroom.query.get_or_404(id)
    classroom.name = data.get('name', classroom.name)
    classroom.capacity = data.get('capacity', classroom.capacity)
    kanvas_db.session.commit()
    return render_template('classrooms/edit.html', classroom=classroom)

@classroom_bp.route('/classrooms/<int:id>', methods=['DELETE'])
def delete(id):
    classroom = Classroom.query.get_or_404(id)
    kanvas_db.session.delete(classroom)
    kanvas_db.session.commit()
    return redirect(url_for('classroom.index'))

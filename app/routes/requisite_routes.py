from flask import Blueprint, render_template, request, redirect, url_for
from app import db
from app.models.course import Course
from app.models.requisite import Requisite

requisite_bp = Blueprint('requisite', __name__, url_prefix='/requisites')

@requisite_bp.route('/create', methods=['POST'])
def create():
    course_id = request.form.get('course_id')
    requisite_id = request.form.get('requisite_id')

    if not course_id or not requisite_id:
        print("Debe seleccionar un curso y su requisito.")
        return redirect(url_for('course.show', id=course_id))

    new_requisite = Requisite(course_id=course_id, course_requisite_id=requisite_id)

    try:
        db.session.add(new_requisite)
        db.session.commit()
        print("Requisito añadido con éxito.")
    except Exception as e:
        db.session.rollback()
        print(f"Error al crear el requisito: {e}")

    return redirect(url_for('course.show', id=course_id))

@requisite_bp.route('/delete/<int:id>')
def delete(id):
    requisite = Requisite.query.get_or_404(id)
    course_id = requisite.course_id
    
    try:
        db.session.delete(requisite)
        db.session.commit()
        print("Requisito eliminado con éxito.")
    except Exception as e:
        db.session.rollback()
        print(f"Error al eliminar el requisito: {e}")
    
    return redirect(url_for('course.show', id=course_id))
from flask import Blueprint, render_template, request, redirect, url_for, flash
from app import kanvas_db
from app.models.course import Course
from app.models.course_instance import CourseInstance

course_instance_bp = Blueprint('course_instance', __name__, url_prefix='/course_instances')

@course_instance_bp.route('/')
def index():
    course_instances = CourseInstance.query.all()
    return render_template('course_instances/index.html', course_instances=course_instances)

@course_instance_bp.route('/<int:id>')
def show(id):
    course_instance = CourseInstance.query.get_or_404(id)
    return render_template('course_instances/show.html', course_instance=course_instance)

@course_instance_bp.route('/create', methods=['GET', 'POST'])
def create():
    if request.method == 'POST':
        course_id = request.form.get('course_id')
        year = request.form.get('year')
        semester = request.form.get('semester')

        if not course_id or not year or not semester:
            flash("Todos los campos son obligatorios.", "warning")
        else:
            new_course_instance = CourseInstance(course_id=course_id, year=year, semester=semester)
            try:
                kanvas_db.session.add(new_course_instance)
                kanvas_db.session.commit()
                flash("Instancia del curso creada exitosamente.", "success")
                return redirect(url_for('course_instance.index'))
            except Exception as e:
                kanvas_db.session.rollback()
                flash(f"Error al crear la instancia del curso: {str(e)}", "danger")

    courses = Course.query.all()
    return render_template('course_instances/create.html', courses=courses)

@course_instance_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    course_instance = CourseInstance.query.get_or_404(id)
    
    if request.method == 'POST':
        course_id = request.form.get('course_id')
        year = request.form.get('year')
        semester = request.form.get('semester')

        if not course_id or not year or not semester:
            flash("Todos los campos son obligatorios.", "warning")
        else:
            course_instance.course_id = course_id
            course_instance.year = year
            course_instance.semester = semester
            try:
                kanvas_db.session.commit()
                flash("Instancia del curso editada exitosamente.", "success")
                return redirect(url_for('course_instance.index'))
            except Exception as e:
                kanvas_db.session.rollback()
                flash(f"Error al editar la instancia del curso: {str(e)}", "danger")

    courses = Course.query.all()
    return render_template('course_instances/edit.html', course_instance=course_instance, courses=courses)

@course_instance_bp.route('/delete/<int:id>', methods=['POST'])
def delete(id):
    course_instance = CourseInstance.query.get_or_404(id)
    try:
        kanvas_db.session.delete(course_instance)
        kanvas_db.session.commit()
        flash("Instancia del curso eliminada con éxito.", "success")
    except Exception as e:
        kanvas_db.session.rollback()
        flash(f"Error deleting course_instance: {e}", "danger")
        return redirect(url_for('course_instance.show', id=id))
    
    return redirect(url_for('course_instance.index'))

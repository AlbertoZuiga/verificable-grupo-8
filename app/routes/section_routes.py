from flask import Blueprint, render_template, request, redirect, url_for, flash
from app import kanvas_db
from app.models import CourseInstance, Section, WeighingType, Teacher
from app.services.section_service import create_section

section_bp = Blueprint('section', __name__, url_prefix='/sections')

@section_bp.route('/')
def index():
    sections = Section.query.all()
    return render_template('sections/index.html', sections=sections)

@section_bp.route('/<int:id>')
def show(id):
    section = Section.query.get_or_404(id)
    return render_template('sections/show.html', section=section, WeighingType=WeighingType)

@section_bp.route('/create', methods=['GET', 'POST'])
def create():
    if request.method == 'POST':
        course_instance_id = request.form['course_instance_id']
        teacher_id = request.form['teacher_id']
        code = request.form['code']
        weighing_type = request.form['weighing_type']

        try:
            create_section(course_instance_id, teacher_id, code, weighing_type)
            flash("Sección creada exitosamente", "success")
            return redirect(url_for('section.index'))
        except ValueError as ve:
            flash(str(ve), "warning")
        except Exception as e:
            flash("Error al crear la sección", "danger")
            print(f"Error al crear la sección: {str(e)}")

    course_instances = CourseInstance.query.all()
    teachers = Teacher.query.all()
    context = {
        "course_instances": course_instances,
        "weighing_types": WeighingType,
        "teachers": teachers
    }
    return render_template('sections/create.html', **context)

@section_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    section = Section.query.get_or_404(id)

    if request.method == 'POST':
        course_instance_id = request.form['course_instance_id']
        teacher_id = request.form['teacher_id']
        code = request.form['code']
        weighing_type = request.form['weighing_type']
        
        if not course_instance_id or not teacher_id or not code or not weighing_type:
            print("Todos los campos son obligatorios.")
        else:
            try:
                section.course_instance_id = course_instance_id
                section.teacher_id = teacher_id
                section.code = code
                section.weighing_type = weighing_type
                
                kanvas_db.session.commit()
                print("Sección actualizada exitosamente.")
                return redirect(url_for('section.index'))
            except Exception as e:
                kanvas_db.session.rollback()
                print(f"Error al editar la sección: {str(e)}")

    course_instances = CourseInstance.query.all()
    teachers = Teacher.query.all()

    context = {
        "course_instances": course_instances,
        "weighing_types": WeighingType,
        "teachers": teachers
    }
    return render_template('sections/edit.html', section=section, **context)

@section_bp.route('/delete/<int:id>', methods=['POST'])
def delete(id):
    section = Section.query.get_or_404(id)
    try:
        kanvas_db.session.delete(section)
        kanvas_db.session.commit()
        flash("Sección eliminada con éxito.", "success")
    except Exception as e:
        kanvas_db.session.rollback()
        flash("No se puede eliminar esta sección porque tiene elementos asociados. Elimínalos primero.", "danger")
        print(f"Error deleting section: {e}")
        return redirect(url_for('section.show', id=id))
    
    return redirect(url_for('section.index'))

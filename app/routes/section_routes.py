from flask import Blueprint, render_template, request, redirect, url_for
from app import kanvas_db
from app.models.course_instance import CourseInstance
from app.models.section import Section, WeighingType

section_bp = Blueprint('section', __name__, url_prefix='/sections')

@section_bp.route('/')
def index():
    sections = Section.query.all()
    return render_template('sections/index.html', sections=sections)

@section_bp.route('/<int:id>')
def show(id):
    section = Section.query.get_or_404(id)
    return render_template('sections/show.html', section=section)

@section_bp.route('/create', methods=['GET', 'POST'])
def create():
    if request.method == 'POST':
        course_instance_id = request.form['course_instance_id']
        code = request.form['code']
        weighing_type = request.form['weighing_type']
        
        if not course_instance_id or not code or not weighing_type:
            print("Todos los campos son obligatorios.")
        else:
            new_section = Section(course_instance_id=course_instance_id, code=code, weighing_type=weighing_type)
            try:
                kanvas_db.session.add(new_section)
                kanvas_db.session.commit()
                print("Seccion creada exitosamente")
                return redirect(url_for('section.index'))
            except Exception as e:
                kanvas_db.session.rollback()
                print(f"Error al crear la seccion: {str(e)}")

    course_instances = CourseInstance.query.all()

    context = {
        "course_instances": course_instances,
        "weighing_types": WeighingType
    }
    return render_template('sections/create.html', **context)

@section_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    section = Section.query.get_or_404(id)

    if request.method == 'POST':
        course_instance_id = request.form['course_instance_id']
        code = request.form['code']
        weighing_type = request.form['weighing_type']
        
        if not course_instance_id or not code or not weighing_type:
            print("Todos los campos son obligatorios.")
        else:
            try:
                section.course_instance_id = course_instance_id
                section.code = code
                section.weighing_type = weighing_type
                
                kanvas_db.session.commit()
                print("Sección actualizada exitosamente.")
                return redirect(url_for('section.index'))
            except Exception as e:
                kanvas_db.session.rollback()
                print(f"Error al editar la sección: {str(e)}")

    course_instances = CourseInstance.query.all()

    context = {
        "course_instances": course_instances,
        "weighing_types": WeighingType
    }
    return render_template('sections/edit.html', section=section, **context)

@section_bp.route('/delete/<int:id>')
def delete(id):
    section = Section.query.get_or_404(id)
    try:
        kanvas_db.session.delete(section)
        kanvas_db.session.commit()
    except Exception as e:
        kanvas_db.session.rollback()
        print(f"Error deleting section: {e}")
    return redirect(url_for('section.index'))

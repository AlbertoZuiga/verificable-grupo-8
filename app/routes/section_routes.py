from flask import Blueprint, render_template, request, redirect, url_for
from app import db
from app.models.course_instance import CourseInstance
from app.models.section import Section, WeightingType

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
        weighting_type = request.form['weighting_type']
        
        if not course_instance_id or not code or not weighting_type:
            print("Todos los campos son obligatorios.")
        else:
            new_section = Section(course_instance_id=course_instance_id, code=code, weighting_type=weighting_type)
            try:
                db.session.add(new_section)
                db.session.commit()
                print("Seccion creada exitosamente")
                return redirect(url_for('section.index'))
            except Exception as e:
                db.session.rollback()
                print(f"Error al crear la seccion: {str(e)}")

    course_instances = CourseInstance.query.all()

    context = {
        "course_instances": course_instances,
        "weighting_types": WeightingType
    }
    return render_template('sections/create.html', **context)

@section_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    section = Section.query.get_or_404(id)

    if request.method == 'POST':
        course_instance_id = request.form['course_instance_id']
        code = request.form['code']
        weighting_type = request.form['weighting_type']
        
        if not course_instance_id or not code or not weighting_type:
            print("Todos los campos son obligatorios.")
        else:
            try:
                section.course_instance_id = course_instance_id
                section.code = code
                section.weighting_type = weighting_type
                
                db.session.commit()
                print("Sección actualizada exitosamente.")
                return redirect(url_for('section.index'))
            except Exception as e:
                db.session.rollback()
                print(f"Error al editar la sección: {str(e)}")

    course_instances = CourseInstance.query.all()

    context = {
        "course_instances": course_instances,
        "weighting_types": WeightingType
    }
    return render_template('sections/edit.html', section=section, **context)

@section_bp.route('/delete/<int:id>')
def delete(id):
    section = Section.query.get_or_404(id)
    try:
        db.session.delete(section)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(f"Error deleting section: {e}")
    return redirect(url_for('section.index'))

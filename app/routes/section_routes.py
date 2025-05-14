from flask import Blueprint, render_template, request, redirect, url_for, flash
from app import kanvas_db
from app.models import CourseInstance, Section, WeighingType, Teacher
from app.services.section_service import create_section
from app.services.decorators import require_section_open


section_bp = Blueprint('section', __name__, url_prefix='/sections')

@section_bp.route('/')
def index():
    sections = Section.query.all()
    return render_template('sections/index.html', sections=sections)

@section_bp.route('/<int:id>')
def show(id):
    section = Section.query.get_or_404(id)
    return render_template('sections/show.html', section=section, WeighingType=WeighingType)

@section_bp.route('/<int:id>/edit_evaluation_weights', methods=['GET', 'POST'])
def edit_evaluation_weights(id):
    section = Section.query.get_or_404(id)

    if request.method == 'POST':
        weights = {}
        try:
            for evaluation in section.evaluations:
                key = f'evaluation_{evaluation.id}'
                weights[evaluation.id] = float(request.form[key])
        except (ValueError, KeyError) as e:
            flash(f"Entrada inválida para los pesos: {e}", "danger")
            return redirect(url_for('section.edit_evaluation_weights', id=section.id))

        # Validación para evaluaciones con porcentajes
        if section.weighing_type == WeighingType.PERCENTAGE:
            total = sum(weights.values())
            if round(total, 2) != 100.0:
                flash("La suma de los pesos de las evaluaciones debe ser 100 para las evaluaciones ponderadas.", "danger")
                return redirect(url_for('section.edit_evaluation_weights', id=section.id))

        # Asignar pesos nuevos
        for evaluation in section.evaluations:
            evaluation.weighing = weights[evaluation.id]

        try:
            kanvas_db.session.commit()
            flash("Pesos de evaluaciones actualizados correctamente", "success")
            return redirect(url_for('section.show', id=section.id))
        except Exception as e:
            kanvas_db.session.rollback()
            flash(f"Error al guardar cambios: {e}", "danger")

    return render_template('sections/edit_evaluation_weights.html', section=section, WeighingType=WeighingType)

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
@require_section_open(lambda id: Section.query.get_or_404(id))
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
@require_section_open(lambda id: Section.query.get_or_404(id))
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

@section_bp.route('/<int:section_id>/close', methods=['POST'])
def close(section_id):
    section = Section.query.get_or_404(section_id)
    section.closed = True
    kanvas_db.session.commit()
    flash("La sección fue cerrada exitosamente.", "success")
    return redirect(url_for('section.index', section_id=section.id))


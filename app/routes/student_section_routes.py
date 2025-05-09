from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from app import kanvas_db
from app.models import Section
from app.models import StudentSection

from app.services.student_section_service import get_students_not_in_section, add_student_to_section, remove_student_from_section, add_students_to_section_from_json

student_section_bp = Blueprint('student_section', __name__, url_prefix='/sections/<int:section_id>/students/')

@student_section_bp.route('/')
def index(section_id):
    section = Section.query.get_or_404(section_id)
    student_sections = StudentSection.query.filter_by(section_id=section_id).all()
    return render_template('student_sections/index.html', section=section, student_sections=student_sections)

@student_section_bp.route('/add', methods=['GET', 'POST'])
def add_user(section_id):
    section = Section.query.get_or_404(section_id)
    students = get_students_not_in_section(section_id)

    if request.method == 'POST':
        student_id = request.form['student_id']

        if not student_id:
            flash("Todos los campos son obligatorios.", "danger")
        else:
            if add_student_to_section(student_id, section_id):
                flash("Usuario agregado exitosamente.", "success")
            else:
                flash("El estudiante ya está en esta sección.", "warning")

    context = {
        'section': section,
        'students': students
    }
    return render_template('student_sections/add.html', **context)

@student_section_bp.route('/remove/<int:student_id>', methods=['POST'])
def remove_user(section_id, student_id):
    if remove_student_from_section(section_id, student_id):
        flash("Usuario removido de la sección.", "success")
    else:
        flash("Error al remover usuario de la sección.", "danger")
    return redirect(url_for('student_section.index', section_id=section_id))


@student_section_bp.route('/bulk_load_json', methods=['POST'])
def bulk_load_students_json(section_id=None, **kwargs):
    json_payload = request.get_json()

    if not json_payload or 'alumnos_seccion' not in json_payload:
        return jsonify({'error': 'Invalid JSON format'}), 400

    student_section_entries = json_payload['alumnos_seccion']
    total_students_added = 0
    failed_entries = []

    for entry in student_section_entries:
        section_id = entry.get('seccion_id')
        student_id = entry.get('alumno_id')

        if section_id is None or student_id is None:
            failed_entries.append(f"Missing section_id or student_id in entry: {entry}")
            continue

        try:
            was_added = add_student_to_section(student_id=student_id, section_id=section_id)
            if was_added:
                total_students_added += 1
        except Exception as error:
            error_message = f"Error adding student {student_id} to section {section_id}: {str(error)}"
            failed_entries.append(error_message)

    return jsonify({
        'message': f'{total_students_added} students successfully assigned to sections.',
        'errors': failed_entries
    }), 200




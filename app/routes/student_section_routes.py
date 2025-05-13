from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from app import kanvas_db
from app.models import Section
from app.models import StudentSection

from app.services.student_section_service import get_students_not_in_section, add_student_to_section, remove_student_from_section

student_section_bp = Blueprint('student_section', __name__, url_prefix='/sections/<int:section_id>/students/')

@student_section_bp.route('/')
def index(section_id):
    section = Section.query.get_or_404(section_id)
    student_sections = StudentSection.query.filter_by(section_id=section_id).all()
    return render_template('student_sections/index.html', section=section, student_sections=student_sections)

from flask import request, render_template, redirect, url_for, flash
import json

@student_section_bp.route('/add', methods=['GET', 'POST'])
def add_user(section_id):
    section = Section.query.get_or_404(section_id)
    students = get_students_not_in_section(section_id)

    if request.method == 'POST':
        ids_json = request.form.get('student_ids')

        if not ids_json:
            flash("Debes agregar al menos un estudiante.", "danger")
        else:
            try:
                student_ids = json.loads(ids_json)
                added = 0
                for student_id in student_ids:
                    if add_student_to_section(student_id, section_id):
                        added += 1
                if added:
                    flash(f"{added} estudiante(s) agregados exitosamente.", "success")
                else:
                    flash("Los estudiantes ya estaban en esta sección.", "warning")
            except Exception as e:
                flash("Error al procesar los estudiantes.", "danger")
                print("Error:", e)

        return redirect(url_for('student_section.index', section_id=section_id))

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



from flask import Blueprint, render_template, request, redirect, url_for
from app import kanvas_db
from app.models import StudentSection
from app.models import User
from app.models import Student
from app.models import Section

student_section_bp = Blueprint('student_section', __name__, url_prefix='/sections/<int:section_id>/students/')

@student_section_bp.route('/')
def index(section_id):
    section = Section.query.get_or_404(section_id)
    student_sections = StudentSection.query.filter_by(section_id=section_id).all()
    return render_template('student_sections/index.html', section=section, student_sections=student_sections)

@student_section_bp.route('/add', methods=['GET', 'POST'])
def add_user(section_id):
    section = Section.query.get_or_404(section_id)
    section_student_ids = [student.id for student in section.students]

    students = Student.query.filter(Student.id.notin_(section_student_ids)).all()

    if request.method == 'POST':
        student_id = request.form['student_id']

        if not student_id:
            print("Todos los campos son obligatorios.")
        else:
            new_student_section = StudentSection(student_id=student_id, section_id=section_id)
            try:
                kanvas_db.session.add(new_student_section)
                kanvas_db.session.commit()
                print("Usuario agregado exitosamente.")
                return redirect(url_for('student_section.index', section_id=section_id))
            except Exception as e:
                kanvas_db.session.rollback()
                print(f"Error al agregar usuario a la sección: {str(e)}")

    context = {
        'section': section,
        'students': students
    }
    return render_template('student_sections/add.html', **context)

@student_section_bp.route('/remove/<int:student_id>', methods=['POST'])
def remove_user(section_id, student_id):
    student_section = StudentSection.query.filter_by(section_id=section_id, student_id=student_id).first_or_404()
    try:
        kanvas_db.session.delete(student_section)
        kanvas_db.session.commit()
        print("Usuario removido de la sección.")
    except Exception as e:
        kanvas_db.session.rollback()
        print(f"Error al remover usuario de la sección: {e}")
    return redirect(url_for('student_section.index', section_id=section_id))

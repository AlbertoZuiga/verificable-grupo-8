from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from app import kanvas_db
from app.models import User, Student, Teacher, Section, StudentSection
import json

load_json_bp = Blueprint('load_json', __name__, url_prefix='/load_json')

@load_json_bp.route('/')
def index():
    return render_template('load_json/index.html')

def _parse_json_file(json_file, json_type):
    data = json.load(json_file)
    if json_type == "sections":
        return data
    else:
        if json_type not in data:
            raise KeyError(f"'{json_type}' not found in JSON data")
        return data[json_type]

def _process_user(student_data):
    name_parts = student_data['nombre'].split(' ')
    first_name = name_parts[0]
    last_name = ' '.join(name_parts[1:]) if len(name_parts) > 1 else ''

    user = User.query.filter_by(email=student_data['correo']).first()
    if not user:
        user = User(
            first_name=first_name,
            last_name=last_name,
            email=student_data['correo']
        )
        user.set_password(f"password_{student_data['nombre']}")
    else:
        user.first_name = first_name
        user.last_name = last_name

    kanvas_db.session.add(user)
    kanvas_db.session.flush()
    return user

def _process_student(student_data, user_id):
    student = Student.query.filter_by(id=student_data['id']).first()
    if not student:
        student = Student(
            id=student_data['id'],
            user_id=user_id,
            university_entry_year=student_data['anio_ingreso']
        )
    else:
        student.user_id = user_id
        student.university_entry_year = student_data['anio_ingreso']

    kanvas_db.session.add(student)

def _process_teacher(teacher_data, user_id):
    teacher = Teacher.query.filter_by(id=teacher_data['id']).first()
    if not teacher:
        teacher = Teacher(
            id=teacher_data['id'],
            user_id=user_id
        )
    else:
        teacher.user_id = user_id

    kanvas_db.session.add(teacher)

def _add_students_to_section(section_id, student_ids):
    # Buscar la sección
    section = Section.query.get(section_id)
    if not section:
        raise ValueError(f'Section with id {section_id} not found.')

    # Obtener los estudiantes ya asignados a la sección
    existing_ids = {s.id for s in section.students}

    # Crear la lista de nuevas asociaciones (student_section)
    new_links = []
    for student_id in student_ids:
        if student_id not in existing_ids:
            new_links.append(StudentSection(student_id=student_id, section_id=section_id))

    # Si no hay nuevas asociaciones, retornar 0
    if not new_links:
        return 0

    try:
        kanvas_db.session.add_all(new_links)
        kanvas_db.session.commit()
        return len(new_links)
    except Exception as e:
        kanvas_db.session.rollback()
        raise RuntimeError(f'Error al agregar estudiantes a la sección: {str(e)}')

@load_json_bp.route('/students', methods=['GET', 'POST'])
def students():
    if request.method == 'POST':
        json_file = request.files['file']
        json_type = request.form['json_type']

        if json_file and json_file.filename.endswith('.json'):
            try:
                students_data = _parse_json_file(json_file, json_type)
                for student_data in students_data:
                    user = _process_user(student_data)
                    _process_student(student_data, user.id)
                kanvas_db.session.commit()
            except Exception as e:
                kanvas_db.session.rollback()
                return f"Error al cargar JSON: {str(e)}", 400

            flash("Alumnos cargados correctamente!", "success")
            return redirect(url_for('load_json.index'))
    return render_template('load_json/students.html')

@load_json_bp.route('/teachers', methods=['GET', 'POST'])
def teachers():
    if request.method == 'POST':
        json_file = request.files['file']
        json_type = request.form['json_type']

        if json_file and json_file.filename.endswith('.json'):
            try:
                teachers_data = _parse_json_file(json_file, json_type)
                for teacher_data in teachers_data:
                    user = _process_user(teacher_data)
                    _process_teacher(teacher_data, user.id)
                kanvas_db.session.commit()
            except Exception as e:
                kanvas_db.session.rollback()
                return f"Error al cargar JSON: {str(e)}", 400

            flash("Profesores cargados correctamente!", "success")
            return redirect(url_for('load_json.index'))
    return render_template('load_json/teachers.html')

@load_json_bp.route('/assign_students_to_sections', methods=['POST'])
def assign_students_to_sections():
    # Obtener el archivo JSON desde la solicitud
    json_file = request.files.get('file')

    if not json_file or not json_file.filename.endswith('.json'):
        return jsonify({'error': 'No valid JSON file uploaded'}), 400

    try:
        # Cargar los datos del archivo JSON
        json_data = json.load(json_file)
        student_section_entries = json_data.get('alumnos_seccion')

        if not student_section_entries:
            return jsonify({'error': 'Invalid JSON format. Missing "alumnos_seccion".'}), 400

        total_students_added = 0
        failed_entries = []

        # Procesar cada entrada de los estudiantes
        for entry in student_section_entries:
            section_id = entry.get('seccion_id')
            student_ids = entry.get('alumnos_ids', [])

            if not section_id or not student_ids:
                failed_entries.append(f"Missing section_id or student_ids in entry: {entry}")
                continue

            try:
                students_added = _add_students_to_section(section_id, student_ids)
                if students_added:
                    total_students_added += students_added
            except Exception as e:
                failed_entries.append(f"Error assigning students to section {section_id}: {str(e)}")

        return jsonify({
            'message': f'{total_students_added} students successfully assigned to sections.',
            'errors': failed_entries
        }), 200
    except Exception as e:
        return jsonify({'error': f"Error processing the file: {str(e)}"}), 400

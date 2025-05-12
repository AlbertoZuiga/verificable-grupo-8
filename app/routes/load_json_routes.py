from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from app import kanvas_db
from app.models import User, Student, Teacher, Classroom, Course, Requisite, CourseInstance, Semester, Section, WeighingType, StudentSection, StudentEvaluationInstance
from app.services.student_section_service import _add_student_to_section
import json


load_json_bp = Blueprint('load_json', __name__, url_prefix='/load_json')

@load_json_bp.route('/')
def index():
    return render_template('load_json/index.html')

def _parse_json_file(json_file, json_type):
    data = json.load(json_file)
    if json_type=="course instances": # course instances is the only json that has "metadata" (año, semestre)
        return data
    else:
        if json_type not in data:
            raise KeyError(f"'{json_type}' not found in JSON data")
        return data[json_type]

def _process_grade(data):
    instance = StudentEvaluationInstance.query.filter_by(
        student_id=data['alumno_id'],
        evaluation_instance_id=data['instancia'],
        evaluation_id=data['topico_id']
    ).first()

    if not instance:
        instance = StudentEvaluationInstance(
            student_id=data['alumno_id'],
            evaluation_instance_id=data['instancia'],
            evaluation_id=data['topico_id'],
            grade=data['nota']
        )
    else:
        instance.grade = data['nota']

    kanvas_db.session.add(instance)


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

def _process_classroom(data):
    classroom = Classroom.query.filter_by(id=data['id']).first()
    if not classroom:
        classroom = Classroom(
            id=data['id'],
            name=data['nombre'],
            capacity=data['capacidad']
        )
    else:
        classroom.name = data['nombre']
        classroom.capacity = data['capacidad']

    kanvas_db.session.add(classroom)

def _process_course(course_data):
    course = Course.query.filter_by(id=course_data['id']).first()

    if not course:
        course = Course(
            id=course_data['id'],
            code=course_data['codigo'],
            title=course_data['descripcion'], 
            credits=course_data['creditos']
        )
    else:
        course.code = course_data['codigo']
        course.title = course_data['descripcion'] 
        course.credits = course_data['creditos']

    kanvas_db.session.add(course)
    kanvas_db.session.flush()
    
    Requisite.query.filter_by(course_id=course.id).delete()

    for req_code in course_data.get('requisitos', []):
        requisite_course = Course.query.filter_by(code=req_code).first()
        if requisite_course:
            req = Requisite(course_id=course.id, course_requisite_id=requisite_course.id)
            kanvas_db.session.add(req)

def _process_course_instance(data, year, semester):
    instance = CourseInstance.query.filter_by(id=data['id']).first()
    if not instance:
        instance = CourseInstance(
            id=data['id'],
            course_id=data['curso_id'],
            year=year,
            semester=semester
        )
    else:
        instance.course_id = data['curso_id']
        instance.year = year
        instance.semester = semester

    kanvas_db.session.add(instance)

def _process_section(data):
    section = Section.query.filter_by(id=data['id']).first()

    if not section:
        section = Section(
            id=data['id'],
            code=data['id'],  # usando el mismo id como código (ajustar si tienes otro criterio)
            course_instance_id=data['instancia_curso'],
            teacher_id=data['profesor_id'],
            weighing_type=WeighingType.PERCENTAGE  # por ahora usar porcentaje por defecto
        )
    else:
        section.code = data['id']
        section.course_instance_id = data['instancia_curso']
        section.teacher_id = data['profesor_id']
        section.weighing_type = WeighingType.PERCENTAGE

    kanvas_db.session.add(section)

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

@load_json_bp.route('/classrooms', methods=['GET', 'POST'])
def classrooms():
    if request.method == 'POST':
        json_file = request.files['file']
        json_type = request.form['json_type']

        if json_file and json_file.filename.endswith('.json'):
            try:
                classrooms_data = _parse_json_file(json_file, json_type)
                for classroom_data in classrooms_data:
                    _process_classroom(classroom_data)
                kanvas_db.session.commit()
            except Exception as e:
                kanvas_db.session.rollback()
                return f"Error al cargar JSON: {str(e)}", 400

            flash("Salas cargadas correctamente!", "success")
            return redirect(url_for('load_json.index'))
    return render_template('load_json/classrooms.html')

@load_json_bp.route('/courses', methods=['GET', 'POST'])
def courses():
    if request.method == 'POST':
        json_file = request.files['file']
        json_type = request.form['json_type']

        if json_file and json_file.filename.endswith('.json'):
            try:
                courses_data = _parse_json_file(json_file, json_type)
                for course_data in courses_data:
                    _process_course(course_data)
                kanvas_db.session.commit()
            except Exception as e:
                kanvas_db.session.rollback()
                return f"Error al cargar cursos: {str(e)}", 400

            flash("Cursos cargados correctamente!", "success")
            return redirect(url_for('load_json.index'))
    return render_template('load_json/courses.html')

@load_json_bp.route('/course_instances', methods=['GET', 'POST'])
def course_instances():
    if request.method == 'POST':
        json_file = request.files['file']
        json_type = request.form['json_type']

        if json_file and json_file.filename.endswith('.json'):
            try:
                data = _parse_json_file(json_file, json_type)
                year = data["año"]
                semester = Semester(data["semestre"])

                for inst_data in data["instancias"]:
                    _process_course_instance(inst_data, year, semester)

                kanvas_db.session.commit()
            except Exception as e:
                kanvas_db.session.rollback()
                return f"Error al cargar instancias de curso: {str(e)}", 400

            flash("Instancias de curso cargadas correctamente!", "success")
            return redirect(url_for('load_json.index'))
    return render_template('load_json/course_instances.html')

@load_json_bp.route('/sections', methods=['GET', 'POST'])
def sections():
    if request.method == 'POST':
        json_file = request.files['file']
        json_type = request.form['json_type']

        if json_file and json_file.filename.endswith('.json'):
            try:
                sections_data = _parse_json_file(json_file, json_type)
                for section_data in sections_data:
                    _process_section(section_data)
                kanvas_db.session.commit()
            except Exception as e:
                kanvas_db.session.rollback()
                return f"Error al cargar secciones: {str(e)}", 400

            flash("Secciones cargadas correctamente!", "success")
            return redirect(url_for('load_json.index'))
    return render_template('load_json/sections.html')

@load_json_bp.route('/student_sections', methods=['GET', 'POST'])
def student_sections():
    if request.method == 'POST':
        json_file = request.files['file']
        json_type = request.form['json_type']

        if json_file and json_file.filename.endswith('.json'):
            try:
                student_section_data = _parse_json_file(json_file, json_type)

                total_students_added = 0
                for entry in student_section_data:
                    section_id = entry.get('seccion_id')
                    student_ids = entry.get('alumno_id', [])

                    if not section_id or not student_ids:
                        continue

                    added_count = _add_student_to_section(section_id, student_ids)
                    total_students_added += added_count

                kanvas_db.session.commit()
            except Exception as e:
                kanvas_db.session.rollback()
                return f"Error al cargar JSON: {str(e)}", 400

            flash(f"{total_students_added} alumnos asignados a secciones correctamente!", "success")
            return redirect(url_for('load_json.index'))

    return render_template('load_json/student_sections.html')

@load_json_bp.route('/grades', methods=['GET', 'POST'])
def grades():
    if request.method == 'POST':
        json_file = request.files['file']
        json_type = request.form['json_type']

        if json_file and json_file.filename.endswith('.json'):
            try:
                grades_data = _parse_json_file(json_file, json_type)

                for grade in grades_data:
                    _process_grade(grade)

                kanvas_db.session.commit()
            except Exception as e:
                kanvas_db.session.rollback()
                return f"Error al cargar notas: {str(e)}", 400

            flash("Notas cargadas correctamente!", "success")
            return redirect(url_for('load_json.index'))

    return render_template('load_json/grades.html')

from flask import Blueprint, render_template, request, redirect, url_for, flash
from app import kanvas_db
from app.models import User, Student, Teacher, Classroom, Course, Requisite
import json


load_json_bp = Blueprint('load_json', __name__, url_prefix='/load_json')

@load_json_bp.route('/')
def index():
    return render_template('load_json/index.html')

def _parse_json_file(json_file, json_type):
    data = json.load(json_file)
    if json_type=="sections":
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
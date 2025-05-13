import json

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify

from app import kanvas_db
from app.models import (
    User,
    Student,
    Teacher,
    Classroom,
    Course,
    Requisite,
    CourseInstance,
    Semester,
    Section,
    WeighingType,
    StudentSection,
)
from app.services.create_object_instances import create_classroom_instances, create_student_instances, create_teacher_instances, create_course_instances, create_requisite_instances, create_course_instance_objects, create_section_instances, create_evaluation_instances, create_evaluation_instance_instances, create_student_section_instances, create_grade_instances

from app.services.student_section_service import _add_student_to_section
from app.utils import json_constants as JC
from app.utils.parse_json import parse_classroom_json, parse_students_json, parse_teachers_json, parse_courses_json, parse_course_instances_json, parse_sections_json, parse_student_sections_json, parse_grades_json

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

@load_json_bp.route('/students', methods=['GET', 'POST'])
def students():
    if request.method == 'POST':
        json_file = request.files['file']
        json_type = request.form['json_type']

        if json_file and json_file.filename.endswith('.json') and json_type == JC.STUDENTS:
            try:
                file_content = json_file.read().decode('utf-8')
                user_student_pairs = parse_students_json(file_content)

                created_count = create_student_instances(user_student_pairs)
                
                kanvas_db.session.commit()
                flash(f"{created_count} alumnos cargados exitosamente!", "success")
                return redirect(url_for('load_json.index'))

            except Exception as e:
                kanvas_db.session.rollback()
                flash(f"Error loading students: {str(e)}", "danger")
                return f"Error: {str(e)}", 400

    return render_template('load_json/students.html')

@load_json_bp.route('/teachers', methods=['GET', 'POST'])
def teachers():
    if request.method == 'POST':
        json_file = request.files['file']
        json_type = request.form['json_type']

        if json_file and json_file.filename.endswith('.json') and json_type == JC.TEACHERS:
            try:
                file_content = json_file.read().decode('utf-8')
                user_teacher_pairs = parse_teachers_json(file_content)

                created_count = create_teacher_instances(user_teacher_pairs)

                kanvas_db.session.commit()
                flash(f"{created_count} teachers loaded successfully!", "success")
                return redirect(url_for('load_json.index'))

            except Exception as e:
                kanvas_db.session.rollback()
                flash(f"Error loading teachers: {str(e)}", "danger")
                return f"Error: {str(e)}", 400

    return render_template('load_json/teachers.html')

@load_json_bp.route('/classrooms', methods=['GET', 'POST'])
def classrooms():
    if request.method == 'POST':
        json_file = request.files['file']
        json_type = request.form['json_type']

        if json_file and json_file.filename.endswith('.json') and json_type == JC.CLASSROOMS:
            try:
                file_content = json_file.read().decode('utf-8')
                classroom_objects = parse_classroom_json(file_content)
                created_count = create_classroom_instances(classroom_objects)
                kanvas_db.session.commit()
                
                flash(f"{created_count} classrooms loaded successfully!", "success")
                return redirect(url_for('load_json.index'))

            except Exception as e:
                kanvas_db.session.rollback()
                flash(f"Error loading classrooms: {str(e)}", "danger")
                return f"Error: {str(e)}", 400

    return render_template('load_json/classrooms.html')



@load_json_bp.route('/courses', methods=['GET', 'POST'])
def courses():
    if request.method == 'POST':
        json_file = request.files.get('file')
        json_type = request.form.get('json_type')

        if json_file and json_file.filename.endswith('.json') and json_type == JC.COURSES:
            try:
                file_content = json_file.read().decode('utf-8')
                parsed = parse_courses_json(file_content)

                created_courses = create_course_instances(parsed[JC.COURSES])
                kanvas_db.session.flush()  # Ensure course IDs are available

                created_requisites = create_requisite_instances(parsed[JC.REQUISITES])

                kanvas_db.session.commit()
                flash(f"{created_courses} courses and {created_requisites} requisites loaded successfully!", "success")
                return redirect(url_for('load_json.index'))

            except Exception as e:
                kanvas_db.session.rollback()
                flash(f"Error loading courses: {str(e)}", "danger")
                return f"Error: {str(e)}", 400

    return render_template('load_json/courses.html')

@load_json_bp.route('/course_instances', methods=['GET', 'POST'])
def course_instances():
    if request.method == 'POST':
        
        json_file = request.files.get('file')
        json_type = request.form.get('json_type')

        if json_file and json_file.filename.endswith('.json') and json_type == JC.COURSE_INSTANCES:
            try:
                file_content = json_file.read().decode('utf-8')
                parsed_instances = parse_course_instances_json(file_content)

                created_count = create_course_instance_objects(parsed_instances)

                kanvas_db.session.commit()
                flash(f"{created_count} course instances loaded successfully!", "success")
                return redirect(url_for('load_json.index'))

            except Exception as e:
                kanvas_db.session.rollback()
                flash(f"Error loading course instances: {str(e)}", "danger")
                return f"Error: {str(e)}", 400

    return render_template('load_json/course_instances.html')


@load_json_bp.route('/sections', methods=['GET', 'POST'])
def sections():
    if request.method == 'POST':
        json_file = request.files.get('file')
        json_type = request.form.get('json_type')

        if json_file and json_file.filename.endswith('.json') and json_type == JC.SECTIONS:
            try:
                file_content = json_file.read().decode('utf-8')
                parsed_sections, parsed_evaluations, parsed_instances = parse_sections_json(file_content)

                count_sections = create_section_instances(parsed_sections)
                count_evaluations = create_evaluation_instances(parsed_evaluations)
                count_instances = create_evaluation_instance_instances(parsed_instances)

                kanvas_db.session.commit()

                flash(f"{count_sections} sections, {count_evaluations} evaluations, and {count_instances} evaluation instances loaded successfully.", "success")
                return redirect(url_for('load_json.index'))

            except Exception as e:
                kanvas_db.session.rollback()
                flash(f"Error loading sections: {str(e)}", "danger")
                return f"Error: {str(e)}", 400

    return render_template('load_json/sections.html')

@load_json_bp.route('/student_sections', methods=['GET', 'POST'])
def student_sections():
    if request.method == 'POST':
        json_file = request.files.get('file')
        json_type = request.form.get('json_type')

        if json_file and json_file.filename.endswith('.json') and json_type == JC.STUDENT_SECTIONS:
            try:
                file_content = json_file.read().decode('utf-8')
                parsed_links = parse_student_sections_json(file_content)

                created_count = create_student_section_instances(parsed_links)

                kanvas_db.session.commit()
                flash(f"{created_count} student-section assignments loaded successfully!", "success")
                return redirect(url_for('load_json.index'))

            except Exception as e:
                kanvas_db.session.rollback()
                flash(f"Error loading student-section assignments: {str(e)}", "danger")
                return f"Error: {str(e)}", 400

    return render_template('load_json/student_sections.html')


@load_json_bp.route('/grades', methods=['GET', 'POST'])
def grades():
    if request.method == 'POST':
        json_file = request.files.get('file')
        json_type = request.form.get('json_type')

        if json_file and json_file.filename.endswith('.json') and json_type == JC.GRADES:
            try:
                file_content = json_file.read().decode('utf-8')
                grade_objects = parse_grades_json(file_content)

                count = create_grade_instances(grade_objects)

                kanvas_db.session.commit()
                flash(f"{count} grades successfully assigned.", "success")
                return redirect(url_for('load_json.index'))

            except Exception as e:
                kanvas_db.session.rollback()
                flash(f"Error loading grades: {str(e)}", "danger")
                return f"Error: {str(e)}", 400

    return render_template('load_json/grades.html')

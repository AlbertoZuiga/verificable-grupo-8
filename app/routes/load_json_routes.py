from flask import Blueprint, flash, redirect, render_template, request, url_for

from app.models import (
    Classroom,
    Course,
    CourseInstance,
    EvaluationInstance,
    Requisite,
    Section,
    Student,
    StudentEvaluationInstance,
    StudentSection,
    Teacher,
    User,
)

from app import kanvas_db
from app.services.create_object_instances import (
    create_classroom_instances,
    create_course_instance_instances,
    create_course_instances,
    create_evaluation_instance_instances,
    create_evaluation_instances,
    create_grade_instances,
    create_requisite_instances,
    create_section_instances,
    create_student_instances,
    create_student_section_instances,
    create_teacher_instances,
)
from app.utils import json_constants as JC
from app.utils.parse_json import (
    parse_classroom_json,
    parse_courses_json,
    parse_course_instances_json,
    parse_grades_json,
    parse_sections_json,
    parse_student_sections_json,
    parse_students_json,
    parse_teachers_json,
)

from app.services.database_validations import filter_existing_by_field, filter_existing_by_two_fields, filter_grades

from app.utils.flash_messages import flash_successful_load, flash_invalid_grades

load_json_bp = Blueprint('load_json', __name__, url_prefix='/load_json')

@load_json_bp.route('/')
def index():
    return render_template('load_json/index.html')

@load_json_bp.route('/students', methods=['GET', 'POST'])
def students():
    if request.method == 'POST':
        json_file = request.files['file']
        json_type = request.form['json_type']

        if json_file and json_file.filename.endswith('.json') and json_type == JC.STUDENTS:
            try:
                file_content = json_file.read().decode('utf-8')
                user_student_pairs = parse_students_json(file_content)

                # Handled slightly differently to account for two models
                users, students = zip(*user_student_pairs) if user_student_pairs else ([], [])
                filtered_users = filter_existing_by_field(User, "email", users)
                filtered_students = filter_existing_by_field(Student, "id", students)

                filtered_pairs = [
                    (user, student)
                    for (user, student) in user_student_pairs
                    if user in filtered_users and student in filtered_students
                ]

                created_count = create_student_instances(filtered_pairs)

                kanvas_db.session.commit()
                flash_successful_load(created_count, JC.STUDENTS_LABEL)
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

                users, teachers = zip(*user_teacher_pairs) if user_teacher_pairs else ([], [])
                
                filtered_users = filter_existing_by_field(User, "email", users)
                filtered_teachers = filter_existing_by_field(Teacher, "user_id", teachers)

                filtered_pairs = [
                    (user, teacher)
                    for (user, teacher) in user_teacher_pairs
                    if user in filtered_users and teacher in filtered_teachers
                ]

                created_count = create_teacher_instances(filtered_pairs)

                kanvas_db.session.commit()
                flash_successful_load(created_count, JC.TEACHERS_LABEL)
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
                filtered_classrooms = filter_existing_by_field(model=Classroom, field_name="id", objects=classroom_objects)
                created_count = create_classroom_instances(filtered_classrooms)
                kanvas_db.session.commit()
                
                flash_successful_load(created_count, JC.CLASSROOMS_LABEL)
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

                filtered_courses = filter_existing_by_field(
                    model=Course,
                    field_name="id",
                    objects=parsed[JC.COURSES]
                )

                created_courses = create_course_instances(filtered_courses)
                kanvas_db.session.flush()  

                created_requisites = create_requisite_instances(parsed[JC.REQUISITES])

                kanvas_db.session.commit()
                flash_successful_load(created_courses, JC.COURSES_LABEL)
                flash_successful_load(created_requisites, JC.REQUISITES_LABEL)
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

                filtered_instances = filter_existing_by_field(
                    model=CourseInstance,
                    field_name="id",
                    objects=parsed_instances
                )

                created_count = create_course_instance_instances(filtered_instances)

                kanvas_db.session.commit()
                flash_successful_load(created_count, JC.COURSE_INSTANCES_LABEL)
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

                filtered_sections = filter_existing_by_field(
                    model=Section,
                    field_name="id",
                    objects=parsed_sections
                )

                count_sections = create_section_instances(filtered_sections)
                count_evaluations = create_evaluation_instances(parsed_evaluations)
                count_instances = create_evaluation_instance_instances(parsed_instances)

                kanvas_db.session.commit()

                flash_successful_load(count_sections, JC.SECTIONS_LABEL)
                flash_successful_load(count_evaluations, JC.EVALUATIONS_LABEL)
                flash_successful_load(count_instances, JC.EVALUATION_INSTANCES_LABEL)

                return redirect(url_for('load_json.index'))

            except Exception as e:
                kanvas_db.session.rollback()
                flash(f"Error loading sections: {str(e)}", "danger")
                return f"Error: {str(e)}", 400

    return render_template('load_json/sections.html')

from app.models import StudentSection
from app.services.database_validations import filter_existing_by_two_fields
from app.utils.flash_messages import flash_successful_load

@load_json_bp.route('/student_sections', methods=['GET', 'POST'])
def student_sections():
    if request.method == 'POST':
        json_file = request.files.get('file')
        json_type = request.form.get('json_type')

        if json_file and json_file.filename.endswith('.json') and json_type == JC.STUDENT_SECTIONS:
            try:
                file_content = json_file.read().decode('utf-8')
                parsed_links = parse_student_sections_json(file_content)

                filtered_links = filter_existing_by_two_fields(
                    model=StudentSection,
                    field_1="section_id",
                    field_2="student_id",
                    objects=parsed_links
                )

                created_count = create_student_section_instances(filtered_links)

                kanvas_db.session.commit()
                flash_successful_load(created_count, JC.STUDENT_SECTIONS_LABEL)
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
                parsed_data = parse_grades_json(file_content)

                valid_entries = filter_grades(parsed_data)
                flash_invalid_grades(parsed_data)

                created_count = create_grade_instances(valid_entries)

                kanvas_db.session.commit()
                flash_successful_load(created_count, JC.GRADES_LABEL)
                return redirect(url_for('load_json.index'))

            except Exception as e:
                kanvas_db.session.rollback()
                flash(f"Error loading grades: {str(e)}", "danger")
                return f"Error: {str(e)}", 400

    return render_template('load_json/grades.html')
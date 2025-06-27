from flask import Blueprint, redirect, render_template, url_for
from sqlalchemy.exc import SQLAlchemyError

from app import kanvas_db
from app.forms.load_json import UploadJSONForm
from app.models import (
    Classroom,
    Course,
    CourseInstance,
    Requisite,
    Section,
    Student,
    StudentSection,
    Teacher,
    User,
)
from app.services.create_object_instances import (
    add_objects_to_session,
    build_requisite_objects_from_codes,
)
from app.services.database_validations import (
    filter_existing_by_field,
    filter_existing_by_two_fields,
    filter_grades,
)
from app.utils import json_constants as JC
from app.utils.flash_messages import flash_invalid_grades, flash_invalid_load, flash_successful_load
from app.utils.parse_json import (
    parse_classroom_json,
    parse_course_instances_json,
    parse_courses_json,
    parse_grades_json,
    parse_sections_json,
    parse_student_sections_json,
    parse_students_json,
    parse_teachers_json,
)

load_json_bp = Blueprint("load_json", __name__, url_prefix="/load_json")


@load_json_bp.route("/")
def index():
    return render_template("load_json/index.html")


def process_students_json(json_file):
    file_content = json_file.read().decode("utf-8")
    user_student_pairs = parse_students_json(file_content)
    users, students = zip(*user_student_pairs) if user_student_pairs else ([], [])
    filtered_users = filter_existing_by_field(User, "email", users)
    filtered_students = filter_existing_by_field(Student, "id", students)

    filtered_pairs = [
        (user, student)
        for (user, student) in user_student_pairs
        if user in filtered_users and student in filtered_students
    ]
    filtered_student_objects = [student for _, student in filtered_pairs]
    filtered_user_objects = [user for user, _ in filtered_pairs]

    created_students_count = add_objects_to_session(filtered_student_objects)
    add_objects_to_session(filtered_user_objects)

    kanvas_db.session.commit()
    flash_successful_load(created_students_count, JC.STUDENTS_LABEL)


@load_json_bp.route("/students", methods=["GET", "POST"])
def load_students_from_json():
    form = UploadJSONForm()

    if form.validate_on_submit():
        try:
            process_students_json(form.file.data)
            return redirect(url_for("load_json.index"))
        except (ValueError, SQLAlchemyError, UnicodeDecodeError) as e:
            kanvas_db.session.rollback()
            flash_invalid_load(JC.STUDENTS_LABEL, e)
            print(f"Error: {str(e)}", 400)
            return render_template("load_json/students.html", form=form)

    form.json_type.data = JC.STUDENTS
    return render_template("load_json/students.html", form=form)


def process_teachers_json(json_file):
    file_content = json_file.read().decode("utf-8")
    user_teacher_pairs = parse_teachers_json(file_content)
    users, teachers = zip(*user_teacher_pairs) if user_teacher_pairs else ([], [])
    filtered_users = filter_existing_by_field(User, "email", users)
    filtered_teachers = filter_existing_by_field(Teacher, "user_id", teachers)

    filtered_pairs = [
        (user, teacher)
        for (user, teacher) in user_teacher_pairs
        if user in filtered_users and teacher in filtered_teachers
    ]
    filtered_teacher_objects = [teacher for _, teacher in filtered_pairs]
    filtered_user_objects = [user for user, _ in filtered_pairs]

    created_teachers_count = add_objects_to_session(filtered_teacher_objects)
    add_objects_to_session(filtered_user_objects)

    kanvas_db.session.commit()
    flash_successful_load(created_teachers_count, JC.TEACHERS_LABEL)


@load_json_bp.route("/teachers", methods=["GET", "POST"])
def load_teachers_from_json():
    form = UploadJSONForm()
    form.json_type.data = JC.TEACHERS

    if form.validate_on_submit():
        try:
            process_teachers_json(form.file.data)
            return redirect(url_for("load_json.index"))
        except (ValueError, SQLAlchemyError, UnicodeDecodeError) as e:
            kanvas_db.session.rollback()
            flash_invalid_load(JC.TEACHERS_LABEL, e)
            print(f"Error: {str(e)}", 400)
            return render_template("load_json/teachers.html", form=form)

    return render_template("load_json/teachers.html", form=form)


@load_json_bp.route("/classrooms", methods=["GET", "POST"])
def load_classrooms_from_json():
    form = UploadJSONForm()
    form.json_type.data = JC.CLASSROOMS

    if form.validate_on_submit():
        try:
            file_content = form.file.data.read().decode("utf-8")
            classroom_objects = parse_classroom_json(file_content)
            filtered_classrooms = filter_existing_by_field(
                model=Classroom, field_name="id", objects=classroom_objects
            )
            created_classrooms_count = add_objects_to_session(filtered_classrooms)
            kanvas_db.session.commit()

            flash_successful_load(created_classrooms_count, JC.CLASSROOMS_LABEL)
            return redirect(url_for("load_json.index"))

        except (ValueError, SQLAlchemyError, UnicodeDecodeError) as e:
            kanvas_db.session.rollback()
            flash_invalid_load(JC.CLASSROOMS_LABEL, e)
            print(f"Error: {str(e)}", 400)
            return render_template("load_json/classrooms.html", form=form)

    return render_template("load_json/classrooms.html", form=form)


@load_json_bp.route("/courses", methods=["GET", "POST"])
def load_courses_from_json():
    form = UploadJSONForm()
    form.json_type.data = JC.COURSES

    if form.validate_on_submit():
        try:
            file_content = form.file.data.read().decode("utf-8")
            courses, requisite_code_pairs = parse_courses_json(file_content)
            filtered_courses = filter_existing_by_field(Course, "id", courses)
            created_courses_count = add_objects_to_session(filtered_courses)

            kanvas_db.session.flush()

            requisites, _ = build_requisite_objects_from_codes(requisite_code_pairs)
            filtered_requisites = filter_existing_by_two_fields(
                Requisite, "course_id", "course_requisite_id", requisites
            )
            created_requisites_count = add_objects_to_session(filtered_requisites)

            kanvas_db.session.commit()
            flash_successful_load(created_courses_count, JC.COURSES_LABEL)
            flash_successful_load(created_requisites_count, JC.REQUISITES_LABEL)
            return redirect(url_for("load_json.index"))

        except (ValueError, SQLAlchemyError, UnicodeDecodeError) as e:
            kanvas_db.session.rollback()
            flash_invalid_load(JC.COURSES_LABEL, e)
            print(f"Error: {str(e)}", 400)
            return render_template("load_json/courses.html", form=form)

    return render_template("load_json/courses.html", form=form)


@load_json_bp.route("/course_instances", methods=["GET", "POST"])
def load_course_instances_from_json():
    form = UploadJSONForm()
    form.json_type.data = JC.COURSE_INSTANCES

    if form.validate_on_submit():
        try:
            file_content = form.file.data.read().decode("utf-8")
            parsed_instances = parse_course_instances_json(file_content)

            filtered_instances = filter_existing_by_field(
                model=CourseInstance, field_name="id", objects=parsed_instances
            )

            created_courses_count = add_objects_to_session(filtered_instances)

            kanvas_db.session.commit()
            flash_successful_load(created_courses_count, JC.COURSE_INSTANCES_LABEL)
            return redirect(url_for("load_json.index"))

        except (ValueError, SQLAlchemyError, UnicodeDecodeError) as e:
            kanvas_db.session.rollback()
            flash_invalid_load(JC.COURSE_INSTANCES_LABEL, e)
            print(f"Error: {str(e)}", 400)
            return render_template("load_json/course_instances.html", form=form)

    return render_template("load_json/course_instances.html", form=form)


@load_json_bp.route("/sections", methods=["GET", "POST"])
def load_sections_from_json():
    form = UploadJSONForm()
    form.json_type.data = JC.SECTIONS

    if form.validate_on_submit():
        try:
            file_content = form.file.data.read().decode("utf-8")
            parsed_sections, parsed_evaluations, parsed_instances = parse_sections_json(
                file_content
            )

            filtered_sections = filter_existing_by_field(
                model=Section, field_name="id", objects=parsed_sections
            )

            created_sections_count = add_objects_to_session(filtered_sections)
            created_evaluations_count = add_objects_to_session(parsed_evaluations)
            created_evaluation_instances_count = add_objects_to_session(parsed_instances)

            kanvas_db.session.commit()

            flash_successful_load(created_sections_count, JC.SECTIONS_LABEL)
            flash_successful_load(created_evaluations_count, JC.EVALUATIONS_LABEL)
            flash_successful_load(created_evaluation_instances_count, JC.EVALUATION_INSTANCES_LABEL)

            return redirect(url_for("load_json.index"))

        except (ValueError, SQLAlchemyError, UnicodeDecodeError) as e:
            kanvas_db.session.rollback()
            flash_invalid_load(JC.SECTIONS_LABEL, e)
            print(f"Error: {str(e)}", 400)
            return render_template("load_json/sections.html", form=form)

    return render_template("load_json/sections.html", form=form)


@load_json_bp.route("/student_sections", methods=["GET", "POST"])
def load_student_sections_from_json():
    form = UploadJSONForm()
    form.json_type.data = JC.STUDENT_SECTIONS

    if form.validate_on_submit():
        try:
            file_content = form.file.data.read().decode("utf-8")
            parsed_links = parse_student_sections_json(file_content)

            filtered_links = filter_existing_by_two_fields(
                model=StudentSection,
                field_1="section_id",
                field_2="student_id",
                objects=parsed_links,
            )

            created_student_sections_count = add_objects_to_session(filtered_links)

            kanvas_db.session.commit()
            flash_successful_load(created_student_sections_count, JC.STUDENT_SECTIONS_LABEL)
            return redirect(url_for("load_json.index"))

        except (ValueError, SQLAlchemyError, UnicodeDecodeError) as e:
            kanvas_db.session.rollback()
            flash_invalid_load(JC.STUDENT_SECTIONS_LABEL, e)
            print(f"Error: {str(e)}", 400)
            return render_template("load_json/student_sections.html", form=form)

    return render_template("load_json/student_sections.html", form=form)


@load_json_bp.route("/grades", methods=["GET", "POST"])
def load_grades_from_json():
    form = UploadJSONForm()
    form.json_type.data = JC.GRADES

    if form.validate_on_submit():
        try:
            file_content = form.file.data.read().decode("utf-8")
            parsed_data = parse_grades_json(file_content)

            valid_entries = filter_grades(parsed_data)
            flash_invalid_grades(parsed_data)

            created_grades_count = add_objects_to_session(valid_entries)

            kanvas_db.session.commit()
            flash_successful_load(created_grades_count, JC.GRADES_LABEL)
            return redirect(url_for("load_json.index"))

        except (ValueError, SQLAlchemyError, UnicodeDecodeError) as e:
            kanvas_db.session.rollback()
            flash_invalid_load(JC.GRADES_LABEL, e)
            print(f"Error: {str(e)}", 400)
            return render_template("load_json/grades.html", form=form)

    return render_template("load_json/grades.html", form=form)

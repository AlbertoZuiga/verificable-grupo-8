from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from app import kanvas_db
from app.models import Classroom, User, Student, Teacher, Course, Requisite, CourseInstance, Semester, Section, Evaluation, EvaluationInstance, WeighingType, StudentSection, StudentEvaluationInstance
from app.services.database_validations import exists_by_field, exists_by_two_fields
from app.utils import json_constants as JC

def create_classroom_instances(classroom_objects)-> int:
    objects_created_count = 0
    validation_field = "id"
    for object in classroom_objects:
        if not exists_by_field(model=Classroom, field_name=validation_field, value=object.id):
            kanvas_db.session.add(object)
            objects_created_count += 1
        else:
            flash(f"Classroom with ID {object.id} already exists. Skipping creation.", "warning")

    return objects_created_count

def create_student_instances(pairs)-> int:
    created_count = 0
    student_validation_field = "user_id"
    user_validation_field = "email"
    for user, student in pairs:
        if exists_by_field(model=Student, field_name=student_validation_field, value=student.id):
            flash(f"Student with ID {student.id} already exists. Skipping.", "warning")
            continue

        if exists_by_field(model=User, field_name=user_validation_field, value=user.email):
            flash(f"User with email {user.email} already exists. Skipping student creation.", "warning")
            continue

        kanvas_db.session.add(user)
        kanvas_db.session.add(student)
        created_count += 1

    return created_count

def create_teacher_instances(pairs) -> int:
    created_count = 0
    teacher_validation_field = "user_id"
    user_validation_field = "email"

    for user, teacher in pairs:
        if exists_by_field(model=Teacher, field_name=teacher_validation_field, value=teacher.user_id):
            flash(f"Teacher with user_id {teacher.user_id} already exists. Skipping.", "warning")
            continue

        if exists_by_field(model=User, field_name=user_validation_field, value=user.email):
            flash(f"User with email {user.email} already exists. Skipping teacher creation.", "warning")
            continue

        kanvas_db.session.add(user)
        kanvas_db.session.add(teacher)
        created_count += 1

    return created_count

def create_course_instances(course_list) -> int:
    created_count = 0
    for course in course_list:
        if exists_by_field(model=Course, field_name="id", value=course.id):
            flash(f"Course with ID {course.id} already exists. Skipping.", "warning")
            continue

        kanvas_db.session.add(course)
        created_count += 1

    return created_count

def create_requisite_instances(requisite_data_list) -> int:
    created_count = 0
    main_course_column = "course_id"
    requisite_course_column = "course_requisite_id"

    for rel in requisite_data_list:
        main_course = Course.query.filter_by(code=rel[JC.MAIN_COURSE_CODE]).first()
        requisite_course = Course.query.filter_by(code=rel[JC.REQUISITE_CODE]).first()

        if not main_course or not requisite_course:
            flash(f"Skipping requisite: {rel[JC.MAIN_COURSE_CODE]} → {rel[JC.REQUISITE_CODE]} (course not found)", "warning")
            continue

        if exists_by_two_fields(Requisite, main_course_column, main_course.id, requisite_course_column, requisite_course.id):
            flash(f"Requisite {main_course.code} → {requisite_course.code} already exists. Skipping.", "info")
            continue

        kanvas_db.session.add(Requisite(course_id=main_course.id, course_requisite_id=requisite_course.id))
        created_count += 1

    return created_count

def create_course_instance_objects(course_instances)-> int:
    created_count = 0
    for instance in course_instances:
        if exists_by_field(CourseInstance, "id", instance.id):
            flash(f"CourseInstance with ID {instance.id} already exists. Skipping.", "warning")
            continue

        kanvas_db.session.add(instance)
        created_count += 1

    return created_count

def create_section_instances(sections)-> int:
    created_count = 0
    for section in sections:
        if exists_by_field(Section, "id", section.id):
            flash(f"Section with ID {section.id} already exists. Skipping.", "warning")
            continue
        kanvas_db.session.add(section)
        created_count += 1
    return created_count

def create_evaluation_instances(evaluations)-> int:
    created_count = 0
    for evaluation in evaluations:
        kanvas_db.session.add(evaluation)
        created_count += 1
    return created_count

def create_evaluation_instance_instances(instances)-> int:
    created_count = 0
    for instance in instances:
        kanvas_db.session.add(instance)
        created_count += 1
    return created_count

def create_student_section_instances(student_section_links)-> int:
    created_count = 0
    for link in student_section_links:
        if exists_by_two_fields(
            StudentSection,
            "section_id", link.section_id,
            "student_id", link.student_id
        ):
            flash(f"Student {link.student_id} already assigned to section {link.section_id}. Skipping.", "warning")
            continue
        kanvas_db.session.add(link)
        created_count += 1
    return created_count

def create_grade_instances(parsed_data)-> int:
    created_count = 0

    for entry in parsed_data:
        student_id = entry["student_id"]
        topic_id = entry["topic_id"]
        instance_index = entry["instance_index"]
        grade = entry["grade"]

        eval_instance = EvaluationInstance.query.filter_by(
            evaluation_id=topic_id,
            index_in_evaluation=instance_index
        ).first()

        if not eval_instance:
            flash(f"No EvaluationInstance found for topic ID {topic_id} and index {instance_index}. Skipping.", "warning")
            continue

        kanvas_db.session.add(
            StudentEvaluationInstance(
                evaluation_instance_id=eval_instance.id,
                student_id=student_id,
                grade=grade
            )
        )
        created_count += 1

    return created_count
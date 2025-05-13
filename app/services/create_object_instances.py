from flask import flash

from app import kanvas_db
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
from app.services.database_validations import exists_by_field, exists_by_two_fields
from app.utils import json_constants as JC

def create_classroom_instances(classroom_objects)-> int:
    objects_created_count = 0
    for object in classroom_objects:
        kanvas_db.session.add(object)
        objects_created_count += 1
    return objects_created_count

def create_student_instances(pairs) -> int:
    created_count = 0
    for user, student in pairs:
        kanvas_db.session.add(user)
        kanvas_db.session.add(student)
        created_count += 1

    return created_count

def create_teacher_instances(pairs) -> int:
    created_count = 0
    for user, teacher in pairs:
        kanvas_db.session.add(user)
        kanvas_db.session.add(teacher)
        created_count += 1
    return created_count

def create_course_instances(course_list) -> int:
    created_count = 0
    for course in course_list:
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

def create_course_instance_instances(course_instances) -> int:
    created_count = 0
    for instance in course_instances:
        kanvas_db.session.add(instance)
        created_count += 1
    return created_count

def create_section_instances(sections) -> int:
    created_count = 0
    for section in sections:
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

def create_student_section_instances(student_section_links) -> int:
    created_count = 0
    for link in student_section_links:
        kanvas_db.session.add(link)
        created_count += 1
    return created_count

# Created to handle grades, which is a special case
def create_grade_instances(validated_entries) -> int:
    created_count = 0
    for entry in validated_entries:
        kanvas_db.session.add(
            StudentEvaluationInstance(
                evaluation_instance_id=entry["evaluation_instance_id"],
                student_id=entry["student_id"],
                grade=entry["grade"]
            )
        )
        created_count += 1
    return created_count
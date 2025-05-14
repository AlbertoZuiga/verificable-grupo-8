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

def add_objects_to_session(instances) -> int:
    objects_created_count = 0
    for instance in instances:
        kanvas_db.session.add(instance)
        objects_created_count += 1
    return objects_created_count
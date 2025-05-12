from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from app import kanvas_db
from app.models import Classroom
from app.services.database_validations import classroom_exists, student_exists, user_exists

def create_classroom_instances(classroom_objects):
    objects_created_count = 0
    for object in classroom_objects:
        if not classroom_exists(object.id):
            kanvas_db.session.add(object)
            objects_created_count += 1
        else:
            flash(f"Classroom with ID {object.id} already exists. Skipping creation.", "warning")

    return objects_created_count



def create_student_instances(pairs):
    created_count = 0

    # Logic slightly different due to dependency on User
    for user, student in pairs:
        if student_exists(student.id):
            flash(f"Student with ID {student.id} already exists. Skipping.", "warning")
            continue

        if user_exists(user.email):
            flash(f"User with email {user.email} already exists. Skipping student creation.", "warning")
            continue

        kanvas_db.session.add(user)
        kanvas_db.session.add(student)
        created_count += 1

    return created_count

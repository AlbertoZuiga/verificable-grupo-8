import pytest
from flask import url_for
from sqlalchemy.exc import IntegrityError

import tests.utils.user_routes_common as common
from app.models.student import Student
from app.models.user import User

# Configuración específica para estudiantes
ENDPOINT = "student"
ENTITY_ID_NAME = "student_id"
LIST_EMPTY_MSG = b"No hay alumnos disponibles."


def extract_form_data(response):
    return common.common_extract_fields(
        response, ["first_name", "last_name", "email", "university_entry_year"]
    )


# ---- Pruebas para index() ----
def test_index_with_multiple_students(client, test_student, test_student2):
    common.common_test_index_with_multiple(client, ENDPOINT, test_student, test_student2)


def test_index_empty(client, _db):
    common.common_test_index_empty(client, ENDPOINT, LIST_EMPTY_MSG)


# ---- Pruebas para show() ----
def test_show_valid_student(client, test_student):
    common.common_test_show_valid(client, ENDPOINT, ENTITY_ID_NAME, test_student.id, test_student)


def test_show_nonexistent_student(client, _db):
    common.common_test_show_nonexistent(client, ENDPOINT, ENTITY_ID_NAME)


# ---- Pruebas para create() ----
def test_create_student_success(client, _db):
    data = {
        "first_name": "Ana",
        "last_name": "García",
        "email": "ana.garcia@example.com",
        "password": "SecurePass123!",
        "password_confirm": "SecurePass123!",
        "university_entry_year": "2023",
    }
    response = client.post(url_for("student.create"), data=data, follow_redirects=True)
    assert response.status_code == 200
    assert "Ana García".encode("utf-8") in response.data

    # Verificar creación en cascada de User
    student = Student.query.filter_by(
        user=User.query.filter_by(email=data["email"]).first()
    ).first()
    assert student is not None
    assert student.university_entry_year == 2023


def test_create_duplicate_email(client, test_student_user):
    data = {
        "first_name": "Juan",
        "last_name": "Perez",
        "email": test_student_user.email,
        "password": "Pass123!",
        "password_confirm": "Pass123!",
        "university_entry_year": "2024",
    }
    common.common_test_create_duplicate_email(client, ENDPOINT, data, test_student_user, 1)


def test_create_invalid_entry_year(client, _db):
    data = {
        "first_name": "Maria",
        "last_name": "Lopez",
        "email": "maria@example.com",
        "password": "Pass123!",
        "password_confirm": "Pass123!",
        "university_entry_year": "1800",
    }
    response = client.post(url_for("student.create"), data=data)
    assert "Año debe estar entre ".encode("utf-8") in response.data


# ---- Pruebas para edit() ----
def test_edit_student_success(client, test_student):
    data = {
        "first_name": "Updated",
        "last_name": "Name",
        "email": "updated@example.com",
        "university_entry_year": "2025",
    }

    def extra_assertions(entity, data):
        assert entity.university_entry_year == int(data["university_entry_year"])

    common.common_test_edit_success(
        client, ENDPOINT, ENTITY_ID_NAME, test_student.id, data, test_student, extra_assertions
    )


def test_edit_duplicate_email(client, test_student, test_student2):
    data = {
        "first_name": test_student.user.first_name,
        "last_name": test_student.user.last_name,
        "email": test_student2.user.email,
        "university_entry_year": test_student.university_entry_year,
    }
    common.common_test_edit_duplicate_email(
        client, ENDPOINT, ENTITY_ID_NAME, test_student.id, data, test_student, test_student2
    )


def test_edit_preserve_original_data(client, test_student):
    common.common_test_edit_preserve_original_data(
        client, ENDPOINT, ENTITY_ID_NAME, test_student.id, test_student, extract_form_data
    )


# ---- Pruebas para delete() ----
def test_delete_student_success(client, test_student):
    common.common_test_delete_success(client, ENDPOINT, ENTITY_ID_NAME, test_student.id, Student)


def test_delete_nonexistent_student(client, _db):
    common.common_test_delete_nonexistent(client, ENDPOINT, ENTITY_ID_NAME)


# ---- Pruebas de integridad ----
def test_orphan_user_creation_prevention(_db):
    with pytest.raises(IntegrityError):
        student = Student(university_entry_year=2023)
        _db.session.add(student)
        _db.session.commit()


# ---- Pruebas de regresión ----
def test_edit_without_email_change(client, test_student):
    data = {
        "first_name": "SameEmail",
        "last_name": "Test",
        "email": test_student.user.email,
        "university_entry_year": "2025",
    }
    common.common_test_edit_without_email_change(
        client, ENDPOINT, ENTITY_ID_NAME, test_student.id, test_student, data
    )

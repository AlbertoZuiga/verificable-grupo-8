import pytest
from flask import url_for
from sqlalchemy.exc import IntegrityError

import tests.utils.user_routes_common as common
from app.models.teacher import Teacher
from app.models.user import User

# Configuración específica para profesores
ENDPOINT = "teacher"
ENTITY_ID_NAME = "teacher_id"
LIST_EMPTY_MSG = b"No hay profesores disponibles."


def extract_form_data(response):
    return common.common_extract_fields(response, ["first_name", "last_name", "email"])


# ---- Pruebas para index() ----
def test_index_with_multiple_teachers(client, test_teacher, test_teacher2):
    common.common_test_index_with_multiple(client, ENDPOINT, test_teacher, test_teacher2)


def test_index_empty(client, _db):
    common.common_test_index_empty(client, ENDPOINT, LIST_EMPTY_MSG)


# ---- Pruebas para show() ----
def test_show_valid_teacher(client, test_teacher):
    common.common_test_show_valid(client, ENDPOINT, ENTITY_ID_NAME, test_teacher.id, test_teacher)


def test_show_nonexistent_teacher(client, _db):
    common.common_test_show_nonexistent(client, ENDPOINT, ENTITY_ID_NAME)


# ---- Pruebas para create() ----
def test_create_teacher_success(client, _db):
    data = {
        "first_name": "Ana",
        "last_name": "García",
        "email": "ana.garcia@example.com",
        "password": "SecurePass123!",
        "password_confirm": "SecurePass123!",
    }
    response = client.post(url_for("teacher.create"), data=data, follow_redirects=True)
    assert response.status_code == 200
    assert "Ana García".encode("utf-8") in response.data

    # Verificar creación en cascada de User
    teacher = Teacher.query.filter_by(
        user=User.query.filter_by(email=data["email"]).first()
    ).first()
    assert teacher is not None


def test_create_duplicate_email(client, test_teacher_user):
    data = {
        "first_name": "Juan",
        "last_name": "Perez",
        "email": test_teacher_user.email,
        "password": "Pass123!",
        "password_confirm": "Pass123!",
    }
    common.common_test_create_duplicate_email(client, ENDPOINT, data, test_teacher_user, 1)


# ---- Pruebas para edit() ----
def test_edit_teacher_success(client, test_teacher):
    data = {
        "first_name": "Updated",
        "last_name": "Name",
        "email": "updated@example.com",
    }

    edit_context = {
        "endpoint": ENDPOINT,
        "entity_id_name": ENTITY_ID_NAME,
        "entity_id_value": test_teacher.id,
        "data": data,
        "entity": test_teacher,
    }
    common.common_test_edit_success(client, edit_context)


def test_edit_duplicate_email(client, test_teacher, test_teacher2):
    data = {
        "first_name": test_teacher.user.first_name,
        "last_name": test_teacher.user.last_name,
        "email": test_teacher2.user.email,
    }

    edit_context = {
        "endpoint": ENDPOINT,
        "entity_id_name": ENTITY_ID_NAME,
        "entity_id_value": test_teacher.id,
        "data": data,
        "entity": test_teacher,
        "other_entity": test_teacher2,
    }
    common.common_test_edit_duplicate_email(client, edit_context)


def test_edit_preserve_original_data(client, test_teacher):
    edit_context = {
        "endpoint": ENDPOINT,
        "entity_id_name": ENTITY_ID_NAME,
        "entity_id_value": test_teacher.id,
        "entity": test_teacher,
        "extract_form_data": extract_form_data,
    }

    common.common_test_edit_preserve_original_data(client, edit_context)


# ---- Pruebas para delete() ----
def test_delete_teacher_success(client, test_teacher):
    common.common_test_delete_success(client, ENDPOINT, ENTITY_ID_NAME, test_teacher.id, Teacher)


def test_delete_nonexistent_teacher(client, _db):
    common.common_test_delete_nonexistent(client, ENDPOINT, ENTITY_ID_NAME)


# ---- Pruebas de integridad ----
def test_orphan_user_creation_prevention(_db):
    with pytest.raises(IntegrityError):
        teacher = Teacher()
        _db.session.add(teacher)
        _db.session.commit()


# ---- Pruebas de regresión ----
def test_edit_without_email_change(client, test_teacher):
    data = {
        "first_name": "SameEmail",
        "last_name": "Test",
        "email": test_teacher.user.email,
    }
    edit_context = {
        "endpoint": ENDPOINT,
        "entity_id_name": ENTITY_ID_NAME,
        "entity_id_value": test_teacher.id,
        "entity": test_teacher,
        "data": data,
    }
    common.common_test_edit_without_email_change(client, edit_context)

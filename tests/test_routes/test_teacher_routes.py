import pytest
from flask import url_for
from sqlalchemy.exc import IntegrityError

from app.models.teacher import Teacher
from app.models.user import User

from tests.utils.form_parsers import extract_common_fields

def extract_form_data(response):
    return extract_common_fields(
        response,
        [
            "first_name",
            "last_name",
            "email",
            "university_entry_year"
        ]
    )


# ---- Pruebas para index() ----
def test_index_with_multiple_students(client, test_teacher, test_teacher2):
    response = client.get(url_for("teacher.index"))
    assert response.status_code == 200
    assert str(test_teacher.user.id).encode() in response.data
    assert str(test_teacher2.user.id).encode() in response.data


def test_index_empty(client, _db):
    response = client.get(url_for("teacher.index"))
    assert response.status_code == 200
    assert b"No hay profesores disponibles." in response.data


# ---- Pruebas para show() ----
def test_show_valid_student(client, test_teacher):
    response = client.get(url_for("teacher.show", teacher_id=test_teacher.id))
    assert response.status_code == 200
    assert test_teacher.user.first_name.encode() in response.data


def test_show_nonexistent_student(client, _db):
    response = client.get(url_for("teacher.show", teacher_id=99999))
    assert response.status_code == 404


# ---- Pruebas para create() ----
def test_create_student_success(client, _db):
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


def test_create_duplicate_email(client, test_student_user):
    data = {
        "first_name": "Juan",
        "last_name": "Perez",
        "email": test_student_user.email,
        "password": "Pass123!",
        "password_confirm": "Pass123!",
    }
    response = client.post(url_for("teacher.create"), data=data)
    assert "Correo ya esta registrado por otro usuario.".encode("utf-8") in response.data
    assert User.query.filter_by(email=test_student_user.email).count() == 1


# ---- Pruebas para edit() ----
def test_edit_student_success(client, test_teacher):
    url = url_for("teacher.edit", teacher_id=test_teacher.id)
    data = {
        "first_name": "Updated",
        "last_name": "Name",
        "email": "updated@example.com",
    }
    response = client.post(url, data=data, follow_redirects=True)
    assert response.status_code == 200
    assert b"Estudiante actualizado correctamente." in response.data

    assert test_teacher.user.first_name == "Updated"
    assert test_teacher.user.email == "updated@example.com"


def test_edit_duplicate_email(client, test_teacher, test_teacher2):
    url = url_for("teacher.edit", teacher_id=test_teacher.id)
    data = {
        "first_name": test_teacher.user.first_name,
        "last_name": test_teacher.user.last_name,
        "email": test_teacher2.user.email,
    }
    response = client.post(url, data=data)
    assert b"Correo ya esta registrado por otro usuario." in response.data

    assert User.query.get(test_teacher.user.id).email != test_teacher2.user.email


def test_edit_preserve_original_data(client, test_teacher):
    response = client.get(url_for("teacher.edit", teacher_id=test_teacher.id))
    form_data = extract_form_data(response)

    assert form_data["first_name"] == test_teacher.user.first_name
    assert form_data["last_name"] == test_teacher.user.last_name
    assert form_data["email"] == test_teacher.user.email


# ---- Pruebas para delete() ----
def test_delete_student_success(client, test_teacher):
    teacher_id = test_teacher.id

    response = client.get(url_for("teacher.delete", teacher_id=teacher_id), follow_redirects=True)
    assert response.status_code == 200
    assert Teacher.query.get(teacher_id) is None


def test_delete_nonexistent_student(client, _db):
    response = client.get(url_for("teacher.delete", teacher_id=99999), follow_redirects=True)
    assert response.status_code == 404


# ---- Pruebas de integridad ----
def test_orphan_user_creation_prevention(_db):
    with pytest.raises(IntegrityError):
        teacher = Teacher()
        _db.session.add(teacher)
        _db.session.commit()


# ---- Pruebas de regresión ----
def test_edit_without_email_change(client, test_teacher):
    url = url_for("teacher.edit", teacher_id=test_teacher.id)
    original_email = test_teacher.user.email
    data = {
        "first_name": "SameEmail",
        "last_name": "Test",
        "email": original_email,
    }
    response = client.post(url, data=data, follow_redirects=True)
    assert response.status_code == 200
    assert User.query.get(test_teacher.user.id).email == original_email

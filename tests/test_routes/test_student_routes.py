import pytest
from flask import url_for
from sqlalchemy.exc import IntegrityError

from app.models.student import Student
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
def test_index_with_multiple_students(client, test_student, test_student2):
    response = client.get(url_for("student.index"))
    assert response.status_code == 200
    assert str(test_student.user.id).encode() in response.data
    assert str(test_student2.user.id).encode() in response.data

def test_index_empty(client, _db):
    response = client.get(url_for("student.index"))
    assert response.status_code == 200
    assert b"No hay alumnos disponibles." in response.data

# ---- Pruebas para show() ----
def test_show_valid_student(client, test_student):
    response = client.get(url_for("student.show", student_id=test_student.id))
    assert response.status_code == 200
    assert test_student.user.first_name.encode() in response.data
    assert str(test_student.university_entry_year).encode() in response.data

def test_show_nonexistent_student(client, _db):
    response = client.get(url_for("student.show", student_id=99999))
    assert response.status_code == 404

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
    response = client.post(url_for("student.create"), data=data)
    assert "Correo ya esta registrado por otro usuario.".encode("utf-8") in response.data
    assert User.query.filter_by(email=test_student_user.email).count() == 1

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
    url = url_for("student.edit", student_id=test_student.id)
    data = {
        "first_name": "Updated",
        "last_name": "Name",
        "email": "updated@example.com",
        "university_entry_year": "2025",
    }
    response = client.post(url, data=data, follow_redirects=True)
    assert response.status_code == 200
    assert b"Estudiante actualizado correctamente." in response.data

    assert test_student.user.first_name == "Updated"
    assert test_student.user.email == "updated@example.com"
    assert test_student.university_entry_year == 2025

def test_edit_duplicate_email(client, test_student, test_student2):
    url = url_for("student.edit", student_id=test_student.id)
    data = {
        "first_name": test_student.user.first_name,
        "last_name": test_student.user.last_name,
        "email": test_student2.user.email,
        "university_entry_year": test_student.university_entry_year,
    }
    response = client.post(url, data=data)
    assert b"Correo ya esta registrado por otro usuario." in response.data

    assert User.query.get(test_student.user.id).email != test_student2.user.email

def test_edit_preserve_original_data(client, test_student):
    response = client.get(url_for("student.edit", student_id=test_student.id))
    form_data = extract_form_data(response)

    assert form_data["first_name"] == test_student.user.first_name
    assert form_data["last_name"] == test_student.user.last_name
    assert form_data["email"] == test_student.user.email
    assert form_data["university_entry_year"] == str(test_student.university_entry_year)

# ---- Pruebas para delete() ----
def test_delete_student_success(client, test_student):
    student_id = test_student.id

    response = client.get(
        url_for("student.delete", student_id=student_id), follow_redirects=True
    )
    assert response.status_code == 200
    assert Student.query.get(student_id) is None

def test_delete_nonexistent_student(client, _db):
    response = client.get(url_for("student.delete", student_id=99999), follow_redirects=True)
    assert response.status_code == 404

# ---- Pruebas de integridad ----
def test_orphan_user_creation_prevention(_db):
    with pytest.raises(IntegrityError):
        student = Student(university_entry_year=2023)
        _db.session.add(student)
        _db.session.commit()

# ---- Pruebas de regresión ----
def test_edit_without_email_change(client, test_student):
    url = url_for("student.edit", student_id=test_student.id)
    original_email = test_student.user.email
    data = {
        "first_name": "SameEmail",
        "last_name": "Test",
        "email": original_email,  # Mismo email
        "university_entry_year": "2025",
    }
    response = client.post(url, data=data, follow_redirects=True)
    assert response.status_code == 200
    assert User.query.get(test_student.user.id).email == original_email

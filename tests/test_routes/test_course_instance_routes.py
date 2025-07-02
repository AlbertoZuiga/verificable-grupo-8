from datetime import datetime

import pytest
from flask import get_flashed_messages, url_for
from sqlalchemy.exc import SQLAlchemyError

from app.models.course import Course
from app.models.course_instance import CourseInstance, Semester

current_year = datetime.now().year

# ---------------------------
# Pruebas para INDEX
# ---------------------------


def test_index_with_no_course_instances(client, _db):
    response = client.get(url_for("course_instance.index"))
    assert response.status_code == 200
    assert b"No hay instancias de cursos" in response.data


def test_index_with_course_instances(client, _db):
    course = Course(title="Matematicas", credits=3, code="MAT101")
    _db.session.add(course)
    _db.session.commit()

    instance = CourseInstance(course_id=course.id, year=2023, semester=Semester.SECOND)
    _db.session.add(instance)
    _db.session.commit()

    response = client.get(url_for("course_instance.index"))
    assert response.status_code == 200
    assert b"Matematicas" in response.data
    assert b"2023" in response.data


# ---------------------------
# Pruebas para SHOW
# ---------------------------


def test_show_existing_course_instance(client, _db):
    course = Course(title="Fisica", credits=3, code="FIS101")
    _db.session.add(course)
    _db.session.commit()

    instance = CourseInstance(course_id=course.id, year=2024, semester=Semester.FIRST)
    _db.session.add(instance)
    _db.session.commit()

    response = client.get(url_for("course_instance.show", course_instance_id=instance.id))
    assert response.status_code == 200
    assert b"Fisica" in response.data
    assert b"2024" in response.data


def test_show_non_existing_course_instance(client, _db):
    response = client.get(url_for("course_instance.show", course_instance_id=9999))
    assert response.status_code == 404


# ---------------------------
# Pruebas para CREATE
# ---------------------------


def test_create_course_instance_success(client, _db):
    course = Course(title="Programacion", credits=3, code="PRO101")
    _db.session.add(course)
    _db.session.commit()

    data = {"course_id": course.id, "year": 2023, "semester": "SECOND"}

    response = client.post(url_for("course_instance.create"), data=data, follow_redirects=True)

    assert response.status_code == 200
    assert b"Programacion" in response.data
    assert b"2023" in response.data

    # Verificar creación en DB
    instance = CourseInstance.query.first()
    assert instance is not None
    assert instance.course_id == course.id
    assert instance.year == 2023
    assert instance.semester == Semester.SECOND


def test_create_duplicate_course_instance(client, _db):
    with client:
        course = Course(title="Biologia", credits=3, code="BIO101")
        _db.session.add(course)
        _db.session.commit()

        instance = CourseInstance(course_id=course.id, year=2023, semester=Semester.FIRST)
        _db.session.add(instance)
        _db.session.commit()

        data = {"course_id": course.id, "year": 2023, "semester": "FIRST"}

        response = client.post(url_for("course_instance.create"), data=data)

        messages = get_flashed_messages()
        assert "Ya existe la instancia de curso." in messages
        assert response.status_code == 200

        instances = CourseInstance.query.filter_by(course_id=course.id).all()
        assert len(instances) == 1


@pytest.mark.parametrize(
    "year, semester, expected_errors",
    [
        ("", "FIRST", ["El año es obligatorio."]),
        (
            str(current_year - 6),
            "FIRST",
            [f"El año debe estar entre {current_year - 5} y {current_year + 5}."],
        ),
        (
            str(current_year + 6),
            "FIRST",
            [f"El año debe estar entre {current_year - 5} y {current_year + 5}."],
        ),
        (str(current_year), "INVALID", ["El semestre seleccionado no es válido."]),
        ("", "INVALID", ["El año es obligatorio.", "El semestre seleccionado no es válido."]),
        (
            str(current_year - 6),
            "INVALID",
            [
                f"El año debe estar entre {current_year - 5} y {current_year + 5}.",
                "El semestre seleccionado no es válido.",
            ],
        ),
        ("dosmilveinticuatro", "FIRST", ["El año es obligatorio."]),
    ],
)
def test_create_with_invalid_data(client, _db, year, semester, expected_errors):
    course = Course(title="Quimica", credits=3, code="QUI101")
    _db.session.add(course)
    _db.session.commit()

    data = {"course_id": course.id, "year": year, "semester": semester}
    response = client.post(url_for("course_instance.create"), data=data)

    assert response.status_code == 200
    html = response.data.decode()

    for error in expected_errors:
        assert error in html

    # Verificar que no se creó nada
    instances = CourseInstance.query.all()
    assert len(instances) == 0


# ---------------------------
# Pruebas para EDIT
# ---------------------------


def test_edit_course_instance_success(client, _db):
    course1 = Course(title="Historia", credits=3, code="HIS101")
    course2 = Course(title="Arte", credits=3, code="ART101")
    _db.session.add_all([course1, course2])
    _db.session.commit()

    instance = CourseInstance(course_id=course1.id, year=2022, semester=Semester.FIRST)
    _db.session.add(instance)
    _db.session.commit()

    data = {"course_id": course2.id, "year": 2023, "semester": "SECOND"}

    response = client.post(
        url_for("course_instance.edit", course_instance_id=instance.id),
        data=data,
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b"Arte" in response.data
    assert b"2023" in response.data

    # Verificar cambios en DB
    updated = CourseInstance.query.get(instance.id)
    assert updated.course_id == course2.id
    assert updated.year == 2023
    assert updated.semester == Semester.SECOND


def test_edit_to_duplicate_instance(client, _db):
    with client:
        course = Course(title="Economia", credits=3, code="ECO101")
        _db.session.add(course)
        _db.session.commit()

        # Crear dos instancias iniciales
        instance1 = CourseInstance(course_id=course.id, year=2023, semester=Semester.SECOND)
        instance2 = CourseInstance(course_id=course.id, year=2024, semester=Semester.FIRST)
        _db.session.add_all([instance1, instance2])
        _db.session.commit()

        data = {"course_id": course.id, "year": 2023, "semester": "SECOND"}

        _response = client.post(
            url_for("course_instance.edit", course_instance_id=instance2.id), data=data
        )

        messages = get_flashed_messages()
        assert "Ya existe la instancia de curso." in messages

        unchanged = CourseInstance.query.get(instance2.id)
        assert unchanged.year == 2024
        assert unchanged.semester == Semester.FIRST


# ---------------------------
# Pruebas para DELETE
# ---------------------------


def test_delete_course_instance_success(client, _db):
    with client:
        course = Course(title="Literatura", credits=3, code="LIT101")
        _db.session.add(course)
        _db.session.commit()

        instance = CourseInstance(course_id=course.id, year=2023, semester=Semester.SECOND)
        _db.session.add(instance)
        _db.session.commit()

        response = client.post(
            url_for("course_instance.delete", course_instance_id=instance.id), follow_redirects=True
        )

        assert response.status_code == 200
        messages = get_flashed_messages()
        assert "Instancia del curso eliminada con éxito." in messages

        deleted = CourseInstance.query.get(instance.id)
        assert deleted is None


def test_delete_non_existing_course_instance(client, _db):
    response = client.post(
        url_for("course_instance.delete", course_instance_id=9999), follow_redirects=True
    )

    assert response.status_code == 404


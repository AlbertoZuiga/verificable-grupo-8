import pytest
from flask import get_flashed_messages, url_for
from sqlalchemy.exc import SQLAlchemyError

from app.models.course import Course


@pytest.fixture(autouse=True)
def setup_db(db):
    course1 = Course(title="Matemáticas", code="MAT101", credits=4)
    course2 = Course(title="Física", code="FIS102", credits=3)
    db.session.add(course1)
    db.session.add(course2)
    db.session.commit()
    yield

    db.session.query(Course).delete()
    db.session.commit()


def test_index_route(client):
    response = client.get(url_for('course.index'))
    assert response.status_code == 200
    assert "Matemáticas".encode() in response.data
    assert "Física".encode() in response.data


def test_show_existing_course(client):
    course = Course.query.first()
    response = client.get(url_for('course.show', course_id=course.id))
    assert response.status_code == 200
    assert course.title.encode() in response.data


def test_show_non_existing_course(client):
    response = client.get(url_for('course.show', course_id=999))
    assert response.status_code == 404


def test_create_course_success(client):
    data = {'title': 'Química', 'code': 'QUI103', 'credits': 4}
    response = client.post(url_for('course.create'), data=data, follow_redirects=True)
    assert response.status_code == 200
    assert b"creada exitosamente" in response.data
    assert Course.query.filter_by(code='QUI103').first() is not None
    assert "Química".encode("utf-8") in response.data


def test_create_duplicate_title(client):
    data = {'title': 'Matemáticas', 'code': 'MAT999', 'credits': 4}
    response = client.post(url_for('course.create'), data=data)
    assert "Ya existe un curso con ese título".encode("utf-8") in response.data
    assert "Matemáticas".encode("utf-8") in response.data


def test_create_duplicate_code(client):
    data = {'title': 'Matemáticas Avanzadas', 'code': 'MAT101', 'credits': 4}
    response = client.post(url_for('course.create'), data=data)
    assert b"Ya existe un curso con ese codigo" in response.data


def test_edit_course_success(client):
    course = Course.query.first()
    data = {
        'title': 'Matemáticas Avanzadas',
        'code': 'MAT201',
        'credits': 5
    }
    with client:
        response = client.post(
            url_for('course.edit', course_id=course.id),
            data=data,
            follow_redirects=True
        )
        messages = get_flashed_messages()
    updated_course = Course.query.get(course.id)

    assert response.status_code == 200
    assert "actualizada exitosamente" in messages[0]
    assert updated_course.title == 'Matemáticas Avanzadas'
    assert updated_course.credits == 5


def test_edit_keep_code_self(client):
    course = Course.query.first()
    data = {
        'title': 'Matemáticas Actualizadas',
        'code': course.code,
        'credits': course.credits
    }
    response = client.post(
        url_for('course.edit', course_id=course.id),
        data=data,
        follow_redirects=True
    )

    assert response.status_code == 200
    assert Course.query.get(course.id).title == 'Matemáticas Actualizadas'


def test_edit_duplicate_code_other_course(client):
    target_course = Course.query.filter_by(code='MAT101').first()

    data = {
        'title': target_course.title,
        'code': 'FIS102',
        'credits': target_course.credits
    }
    with client:
        response = client.post(
            url_for('course.edit', course_id=target_course.id),
            data=data
        )
        messages = get_flashed_messages()

    assert response.status_code == 200
    assert "Ya existe un curso con ese codigo" in messages[0]


def test_delete_course_success(client):
    course = Course.query.first()
    response = client.get(url_for('course.delete', course_id=course.id), follow_redirects=True)
    assert response.status_code == 200
    assert Course.query.get(course.id) is None
    assert "Matemáticas".encode("utf-8") not in response.data


def test_delete_non_existing_course(client):
    response = client.get(url_for('course.delete', course_id=999))
    assert response.status_code == 404


def test_delete_with_db_error(monkeypatch, client, db):
    def mock_commit():
        raise SQLAlchemyError("Error simulado")

    monkeypatch.setattr(db.session, 'commit', mock_commit)

    course = Course.query.first()
    response = client.get(
        url_for('course.delete', course_id=course.id),
        follow_redirects=True
    )

    assert response.status_code == 200
    assert Course.query.get(course.id) is not None

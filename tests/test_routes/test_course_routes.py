# pylint: disable=redefined-outer-name
import pytest
from sqlalchemy import select

from app import create_app
from app.extensions import kanvas_db
from app.models.course import Course


@pytest.fixture
def client():
    app = create_app(testing=True)
    with app.app_context():
        with app.test_client() as test_client:
            kanvas_db.create_all()
        yield test_client

def test_index_shows_courses(client):
    course = Course(title="Algebra", code="MATH101", credits=4)
    kanvas_db.session.add(course)
    kanvas_db.session.commit()

    response = client.get("/courses/")
    assert response.status_code == 200
    assert b"Algebra" in response.data

def test_create_course(client):
    response = client.post(
        "/courses/create",
        data={"title": "Fisica", "code": "PHYS101", "credits": 5},
        follow_redirects=True
    )

    assert response.status_code == 200
    assert b"Instancia del curso creada exitosamente." in response.data

    stmt = select(Course).where(Course.title == "Fisica")
    result = kanvas_db.session.execute(stmt).scalars().first()
    assert result is not None

def test_delete_course(client):
    course = Course(title="Quimica", code="CHEM101", credits=3)
    kanvas_db.session.add(course)
    kanvas_db.session.commit()

    response = client.get(
        f"/courses/delete/{course.id}",
        follow_redirects=True
    )
    assert response.status_code == 200

    deleted_course = kanvas_db.session.get(Course, course.id)
    assert deleted_course is None

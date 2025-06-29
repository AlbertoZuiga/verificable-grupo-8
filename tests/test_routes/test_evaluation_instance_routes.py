# pylint: disable=redefined-outer-name
import pytest
from flask import get_flashed_messages, url_for
from sqlalchemy.exc import SQLAlchemyError

from app.models.course import Course
from app.models.course_instance import CourseInstance, Semester
from app.models.evaluation import Evaluation
from app.models.evaluation_instance import EvaluationInstance
from app.models.section import Section, WeighingType
from app.models.teacher import Teacher
from app.models.user import User


@pytest.fixture
def user(_db):
    user = User(first_name="John", last_name="Doe", email="john_doe@example.com")
    user.set_password("password")
    _db.session.add(user)
    _db.session.commit()
    return user


@pytest.fixture
def teacher(_db, user):
    teacher = Teacher(user_id=user.id)
    _db.session.add(teacher)
    _db.session.commit()
    return teacher


@pytest.fixture
def course(_db):
    course = Course(title="Course Title", code="CODE", credits=3)
    _db.session.add(course)
    _db.session.commit()
    return course


@pytest.fixture
def course_instance(_db, course):
    ci = CourseInstance(course_id=course.id, year=2025, semester=Semester.FIRST)
    _db.session.add(ci)
    _db.session.commit()
    return ci


@pytest.fixture
def open_section(_db, course_instance, teacher):
    section = Section(
        course_instance_id=course_instance.id,
        teacher_id=teacher.id,
        code=1234,
        closed=False,
        weighing_type=WeighingType.WEIGHT,
    )
    _db.session.add(section)
    _db.session.commit()
    return section


@pytest.fixture
def closed_section(_db, course_instance, teacher):
    section = Section(
        course_instance_id=course_instance.id,
        teacher_id=teacher.id,
        code=1235,
        closed=True,
        weighing_type=WeighingType.WEIGHT,
    )
    _db.session.add(section)
    _db.session.commit()
    return section


@pytest.fixture
def evaluation(_db, open_section):
    evaluation = Evaluation(
        title="Math Exam",
        section_id=open_section.id,
        weighing=1,
        weighing_system=WeighingType.WEIGHT,
    )
    _db.session.add(evaluation)
    _db.session.commit()
    return evaluation


@pytest.fixture
def evaluation_instance(_db, evaluation):
    instance = EvaluationInstance(
        title="Midterm", evaluation_id=evaluation.id, index_in_evaluation=1, instance_weighing=1
    )
    _db.session.add(instance)
    _db.session.commit()
    return instance


# Tests
def test_create_success(client, _db, evaluation):
    data = {"title": "Final Exam", "optional": False, "evaluation_id": evaluation.id}

    response = client.post(url_for("evaluation_instance.create"), data=data, follow_redirects=True)

    assert response.status_code == 200
    assert b"Final Exam" in response.data
    assert EvaluationInstance.query.count() == 1


def test_create_duplicate_title(client, _db, evaluation, evaluation_instance):
    with client:
        data = {
            "title": evaluation_instance.title,
            "optional": True,
            "evaluation_id": evaluation.id,
        }

        _response = client.post(url_for("evaluation_instance.create"), data=data)
        messages = get_flashed_messages()

        assert "ya existe" in messages[0]
        assert EvaluationInstance.query.count() == 1


def test_create_db_error(client, _db, evaluation, mocker):
    with client:
        mocker.patch.object(_db.session, "commit", side_effect=SQLAlchemyError("DB error"))

        data = {"title": "Final Exam", "optional": False, "evaluation_id": evaluation.id}

        _response = client.post(url_for("evaluation_instance.create"), data=data)
        messages = get_flashed_messages()

        assert "Error creating" in messages[0]
        assert EvaluationInstance.query.count() == 0


def test_edit_success(client, _db, evaluation_instance):
    data = {
        "title": "Updated Midterm",
        "optional": True,
        "evaluation_id": evaluation_instance.evaluation_id,
    }

    url = url_for("evaluation_instance.edit", evaluation_instance_id=evaluation_instance.id)
    response = client.post(url, data=data, follow_redirects=True)

    assert response.status_code == 200
    assert b"Updated Midterm" in response.data
    # Actualizar la instancia desde la base de datos
    updated_instance = EvaluationInstance.query.get(evaluation_instance.id)
    assert updated_instance.title == "Updated Midterm"


def test_edit_closed_section(client, _db, closed_section):
    evaluation_test = Evaluation(
        title="Closed Eval",
        section_id=closed_section.id,
        weighing=1,
        weighing_system=WeighingType.WEIGHT,
    )
    _db.session.add(evaluation_test)
    _db.session.commit()

    instance = EvaluationInstance(
        title="Closed Instance",
        evaluation_id=evaluation_test.id,
        index_in_evaluation=1,
        instance_weighing=1,
    )
    _db.session.add(instance)
    _db.session.commit()

    url = url_for("evaluation_instance.edit", evaluation_instance_id=instance.id)
    response = client.get(url)

    assert response.status_code == 302
    assert response.headers["Location"].endswith(
        url_for("section.show", section_id=closed_section.id, _external=False)
    )


def test_edit_duplicate_title(client, _db, evaluation):
    with client:
        instance1 = EvaluationInstance(
            title="Instance 1",
            evaluation_id=evaluation.id,
            index_in_evaluation=1,
            instance_weighing=1,
        )
        instance2 = EvaluationInstance(
            title="Instance 2",
            evaluation_id=evaluation.id,
            index_in_evaluation=2,
            instance_weighing=1,
        )
        _db.session.add_all([instance1, instance2])
        _db.session.commit()

        data = {
            "title": instance2.title,
            "optional": True,
            "evaluation_id": evaluation.id,
        }

        url = url_for("evaluation_instance.edit", evaluation_instance_id=instance1.id)
        _response = client.post(url, data=data)
        messages = get_flashed_messages()

        assert "ya existe" in messages[0]
        # Verificar que el título no cambió
        db_instance1 = EvaluationInstance.query.get(instance1.id)
        assert db_instance1.title == "Instance 1"


def test_delete_success(client, _db, evaluation_instance):
    instance_id = evaluation_instance.id
    url = url_for("evaluation_instance.delete", evaluation_instance_id=instance_id)
    response = client.get(url, follow_redirects=True)

    assert response.status_code == 200
    assert EvaluationInstance.query.get(instance_id) is None


def test_delete_closed_section(client, _db, closed_section):
    evaluation_test = Evaluation(
        title="Closed Eval",
        section_id=closed_section.id,
        weighing=1,
        weighing_system=WeighingType.WEIGHT,
    )
    _db.session.add(evaluation_test)
    _db.session.commit()

    instance = EvaluationInstance(
        title="Closed Instance",
        evaluation_id=evaluation_test.id,
        index_in_evaluation=1,
        instance_weighing=1,
    )
    _db.session.add(instance)
    _db.session.commit()

    instance_id = instance.id
    url = url_for("evaluation_instance.delete", evaluation_instance_id=instance_id)
    response = client.get(url)

    assert response.status_code == 302

    assert response.headers["Location"].endswith(
        url_for("section.show", section_id=closed_section.id, _external=False)
    )
    assert EvaluationInstance.query.get(instance_id) is not None


def test_delete_db_error(client, _db, evaluation_instance, mocker):
    mocker.patch.object(_db.session, "commit", side_effect=SQLAlchemyError("DB error"))

    instance_id = evaluation_instance.id
    url = url_for("evaluation_instance.delete", evaluation_instance_id=instance_id)
    response = client.get(url, follow_redirects=True)

    assert b"Error" not in response.data
    assert EvaluationInstance.query.get(instance_id) is not None


def test_show_success(client, evaluation_instance):
    url = url_for("evaluation_instance.show", evaluation_instance_id=evaluation_instance.id)
    response = client.get(url)

    assert response.status_code == 200
    assert evaluation_instance.title.encode() in response.data


def test_show_not_found(client, _db):
    response = client.get(url_for("evaluation_instance.show", evaluation_instance_id=999))
    assert response.status_code == 404


def test_index_with_instances(client, evaluation_instance):
    response = client.get(url_for("evaluation_instance.index"))

    assert response.status_code == 200
    assert evaluation_instance.title.encode() in response.data


def test_index_empty(client, _db):
    # Eliminar todas las instancias existentes
    EvaluationInstance.query.delete()
    _db.session.commit()

    response = client.get(url_for("evaluation_instance.index"))

    assert response.status_code == 200
    assert b"No hay instancias de evaluaciones disponibles." in response.data

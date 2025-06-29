# pylint: disable=redefined-outer-name
import uuid

import pytest

from app import create_app
from app.extensions import kanvas_db
from app.models.course import Course
from app.models.course_instance import CourseInstance, Semester
from app.models.evaluation import Evaluation
from app.models.evaluation_instance import EvaluationInstance
from app.models.section import Section, WeighingType
from app.models.teacher import Teacher
from app.models.user import User


@pytest.fixture(scope="session")
def app():
    test_app = create_app(testing=True)
    test_app.config.update(
        {"SERVER_NAME": "localhost", "APPLICATION_ROOT": "/", "PREFERRED_URL_SCHEME": "http"}
    )
    with test_app.app_context():
        yield test_app


@pytest.fixture
def _db(app):
    with app.app_context():
        kanvas_db.create_all()
        yield kanvas_db
        kanvas_db.session.remove()
        kanvas_db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def runner(app):
    return app.test_cli_runner()


@pytest.fixture
def test_user(_db):
    email = f"john_doe_{uuid.uuid4().hex}@example.com"
    user = User(first_name="John", last_name="Doe", email=email)
    user.set_password("password")
    _db.session.add(user)
    _db.session.commit()
    return user


@pytest.fixture
def test_teacher(_db, test_user):
    teacher = Teacher(user_id=test_user.id)
    _db.session.add(teacher)
    _db.session.commit()
    return teacher


@pytest.fixture
def test_course(_db):
    course = Course(title="Course Title", code="CODE", credits=3)
    _db.session.add(course)
    _db.session.commit()
    return course


@pytest.fixture
def test_course_instance(_db, test_course):
    course_instance = CourseInstance(course_id=test_course.id, year=2025, semester=Semester.FIRST)
    _db.session.add(course_instance)
    _db.session.commit()
    return course_instance


@pytest.fixture
def test_open_section(_db, test_course_instance, test_teacher):
    open_section = Section(
        course_instance_id=test_course_instance.id,
        teacher_id=test_teacher.id,
        code=1234,
        closed=False,
        weighing_type=WeighingType.WEIGHT,
    )
    _db.session.add(open_section)
    _db.session.commit()
    return open_section


@pytest.fixture
def test_closed_section(_db, test_course_instance, test_teacher):
    closed_section = Section(
        course_instance_id=test_course_instance.id,
        teacher_id=test_teacher.id,
        code=1235,
        closed=True,
        weighing_type=WeighingType.WEIGHT,
    )
    _db.session.add(closed_section)
    _db.session.commit()
    return closed_section


@pytest.fixture
def test_section(test_open_section):
    return test_open_section


@pytest.fixture
def test_evaluation(_db, test_open_section):
    evaluation = Evaluation(
        title="Math Exam",
        section_id=test_open_section.id,
        weighing=1,
        weighing_system=WeighingType.WEIGHT,
    )
    _db.session.add(evaluation)
    _db.session.commit()
    return evaluation


@pytest.fixture
def test_evaluation_instance(_db, test_evaluation):
    evaluation_instance = EvaluationInstance(
        title="Midterm",
        evaluation_id=test_evaluation.id,
        index_in_evaluation=1,
        instance_weighing=1,
    )
    _db.session.add(evaluation_instance)
    _db.session.commit()
    return evaluation_instance

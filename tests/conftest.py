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
from app.models.student import Student
from app.models.student_evaluation_instance import StudentEvaluationInstance
from app.models.student_section import StudentSection
from app.models.teacher import Teacher
from app.models.user import User


# 1. App & DB Setup
@pytest.fixture(scope="session")
def app():
    test_app = create_app(testing=True)
    test_app.config.update(
        {"SERVER_NAME": "localhost", "APPLICATION_ROOT": "/", "PREFERRED_URL_SCHEME": "http"}
    )
    with test_app.app_context():
        yield test_app


@pytest.fixture(scope="function")
def _db(app):
    with app.app_context():
        kanvas_db.create_all()
        yield kanvas_db
        kanvas_db.session.remove()
        kanvas_db.drop_all()


@pytest.fixture(scope="function")
def client(app):
    return app.test_client()


@pytest.fixture(scope="function")
def runner(app):
    return app.test_cli_runner()


# 2. Users & Roles
@pytest.fixture(scope="function")
def test_auth_user(_db):
    email = f"auth_user_{uuid.uuid4().hex}@example.com"
    user = User(first_name="John", last_name="Doe", email=email)
    user.set_password("password")
    _db.session.add(user)
    _db.session.commit()
    return user


@pytest.fixture(scope="function")
def test_teacher_user(_db):
    email = f"teacher_user_{uuid.uuid4().hex}@example.com"
    user = User(first_name="John", last_name="Doe", email=email)
    user.set_password("password")
    _db.session.add(user)
    _db.session.commit()
    return user


@pytest.fixture(scope="function")
def test_teacher(_db, test_teacher_user):
    teacher = Teacher(user_id=test_teacher_user.id)
    _db.session.add(teacher)
    _db.session.commit()
    return teacher


@pytest.fixture(scope="function")
def test_teacher_user2(_db):
    email = f"teacher_user_2_{uuid.uuid4().hex}@example.com"
    user = User(first_name="John", last_name="Doe", email=email)
    user.set_password("password")
    _db.session.add(user)
    _db.session.commit()
    return user


@pytest.fixture(scope="function")
def test_teacher2(_db, test_teacher_user2):
    teacher = Teacher(user_id=test_teacher_user2.id)
    _db.session.add(teacher)
    _db.session.commit()
    return teacher


@pytest.fixture(scope="function")
def test_student_user(_db):
    email = f"student_user_{uuid.uuid4().hex}@example.com"
    user = User(first_name="John", last_name="Doe", email=email)
    user.set_password("password")
    _db.session.add(user)
    _db.session.commit()
    return user


@pytest.fixture(scope="function")
def test_student(_db, test_student_user):
    student = Student(user_id=test_student_user.id, university_entry_year=2025)
    _db.session.add(student)
    _db.session.commit()
    return student


@pytest.fixture(scope="function")
def test_student_user2(_db):
    email = f"student_user_2_{uuid.uuid4().hex}@example.com"
    user = User(first_name="John", last_name="Doe", email=email)
    user.set_password("password")
    _db.session.add(user)
    _db.session.commit()
    return user


@pytest.fixture(scope="function")
def test_student2(_db, test_student_user2):
    student = Student(user_id=test_student_user2.id, university_entry_year=2025)
    _db.session.add(student)
    _db.session.commit()
    return student


# 3. Courses & Sections
@pytest.fixture(scope="function")
def test_course(_db):
    course = Course(title="Course Title", code="CODE", credits=3)
    _db.session.add(course)
    _db.session.commit()
    return course


@pytest.fixture(scope="function")
def test_course3(_db):
    course = Course(title="Curso 3", code="C003", credits=2)
    _db.session.add(course)
    _db.session.commit()
    return course


@pytest.fixture(scope="function")
def test_course2(_db):
    course = Course(title="Curso 2", code="C002", credits=3)
    _db.session.add(course)
    _db.session.commit()
    return course


@pytest.fixture(scope="function")
def test_course_instance(_db, test_course):
    course_instance = CourseInstance(course_id=test_course.id, year=2025, semester=Semester.FIRST)
    _db.session.add(course_instance)
    _db.session.commit()
    return course_instance


@pytest.fixture(scope="function")
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


@pytest.fixture(scope="function")
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


@pytest.fixture(scope="function")
def test_section(test_open_section):
    return test_open_section


# 4. Evaluations
@pytest.fixture(scope="function")
def _test_evaluation(_db, test_open_section):
    evaluation = Evaluation(
        title="Math Exam",
        section_id=test_open_section.id,
        weighing=1,
        weighing_system=WeighingType.WEIGHT,
    )
    _db.session.add(evaluation)
    _db.session.commit()
    return evaluation


@pytest.fixture(scope="function")
def test_evaluation_instance(_db, _test_evaluation):
    evaluation_instance = EvaluationInstance(
        title="Midterm",
        evaluation_id=_test_evaluation.id,
        index_in_evaluation=1,
        instance_weighing=1,
    )
    _db.session.add(evaluation_instance)
    _db.session.commit()
    return evaluation_instance


@pytest.fixture(scope="function")
def test_evaluation_closed_section(_db, test_closed_section):
    evaluation = Evaluation(
        title="Closed Evaluation",
        section_id=test_closed_section.id,
        weighing=1,
        weighing_system=WeighingType.WEIGHT,
    )
    _db.session.add(evaluation)
    _db.session.commit()
    return evaluation


@pytest.fixture(scope="function")
def test_evaluation_instance_closed_section(_db, test_evaluation_closed_section):
    instance = EvaluationInstance(
        title="Closed Instance",
        evaluation_id=test_evaluation_closed_section.id,
        index_in_evaluation=1,
        instance_weighing=1,
    )
    _db.session.add(instance)
    _db.session.commit()
    return instance


# 5. Student <-> Section relations
@pytest.fixture(scope="function")
def _test_student_in_section(_db, test_open_section, test_student):
    association = StudentSection(
        student_id=test_student.id,
        section_id=test_open_section.id,
    )
    _db.session.add(association)
    _db.session.commit()
    _db.session.expire_all()
    return type("Obj", (), {"student": test_student, "teacher": test_open_section.teacher})()


@pytest.fixture(scope="function")
def test_student_in_closed_section(_db, test_closed_section, test_student):
    association = StudentSection(
        student_id=test_student.id,
        section_id=test_closed_section.id,
    )
    _db.session.add(association)
    _db.session.commit()
    _db.session.expire_all()
    return type("Obj", (), {"student": test_student, "teacher": test_closed_section.teacher})()


@pytest.fixture(scope="function")
def test_student_not_in_section(_db):
    email = f"no_section_{uuid.uuid4().hex}@example.com"
    user = User(first_name="No", last_name="Section", email=email)
    user.set_password("password")
    _db.session.add(user)
    _db.session.commit()

    student = Student(user_id=user.id, university_entry_year=2025)
    _db.session.add(student)
    _db.session.commit()
    return student


# 6. Grades
@pytest.fixture(scope="function")
def test_grade(_db, test_evaluation_instance, test_student):
    grade = StudentEvaluationInstance(
        student_id=test_student.id, evaluation_instance_id=test_evaluation_instance.id, grade=7.0
    )
    _db.session.add(grade)
    _db.session.commit()
    return grade


# 7. Schedule testing fixtures
@pytest.fixture(scope="function")
def sample_sections_no_conflict(
    _db, test_course, test_teacher, test_teacher2, test_student, test_student2
):
    ci1 = CourseInstance(course_id=test_course.id, year=2025, semester=Semester.FIRST)
    _db.session.add(ci1)
    _db.session.commit()

    sec1 = Section(
        course_instance_id=ci1.id,
        teacher_id=test_teacher.id,
        code=1001,
        closed=False,
        weighing_type=WeighingType.WEIGHT,
    )
    sec2 = Section(
        course_instance_id=ci1.id,
        teacher_id=test_teacher2.id,
        code=1002,
        closed=False,
        weighing_type=WeighingType.WEIGHT,
    )
    _db.session.add_all([sec1, sec2])
    _db.session.commit()

    _db.session.add_all(
        [
            StudentSection(student_id=test_student.id, section_id=sec1.id),
            StudentSection(student_id=test_student2.id, section_id=sec2.id),
        ]
    )
    _db.session.commit()


@pytest.fixture(scope="function")
def sample_sections_teacher_conflict(_db, test_course, test_teacher):
    ci1 = CourseInstance(course_id=test_course.id, year=2025, semester=Semester.FIRST)
    _db.session.add(ci1)
    _db.session.commit()

    # Mismo profesor, secciones potencialmente con conflicto
    sec1 = Section(
        course_instance_id=ci1.id,
        teacher_id=test_teacher.id,
        code=2001,
        closed=False,
        weighing_type=WeighingType.WEIGHT,
    )
    sec2 = Section(
        course_instance_id=ci1.id,
        teacher_id=test_teacher.id,
        code=2002,
        closed=False,
        weighing_type=WeighingType.WEIGHT,
    )
    _db.session.add_all([sec1, sec2])
    _db.session.commit()


@pytest.fixture(scope="function")
def sample_sections_student_conflict(_db, test_course, test_teacher, test_teacher2, test_student):
    ci1 = CourseInstance(course_id=test_course.id, year=2025, semester=Semester.FIRST)
    _db.session.add(ci1)
    _db.session.commit()

    sec1 = Section(
        course_instance_id=ci1.id,
        teacher_id=test_teacher.id,
        code=3001,
        closed=False,
        weighing_type=WeighingType.WEIGHT,
    )
    sec2 = Section(
        course_instance_id=ci1.id,
        teacher_id=test_teacher2.id,
        code=3002,
        closed=False,
        weighing_type=WeighingType.WEIGHT,
    )
    _db.session.add_all([sec1, sec2])
    _db.session.commit()

    # Estudiante inscrito en ambas secciones (conflicto potencial)
    _db.session.add_all(
        [
            StudentSection(student_id=test_student.id, section_id=sec1.id),
            StudentSection(student_id=test_student.id, section_id=sec2.id),
        ]
    )
    _db.session.commit()


@pytest.fixture(scope="function")
def prepopulated_schedule(_db, test_open_section):
    evaluation = Evaluation(
        title="Eval",
        section_id=test_open_section.id,
        weighing=1,
        weighing_system=WeighingType.WEIGHT,
    )
    _db.session.add(evaluation)
    _db.session.commit()

    instance = EvaluationInstance(
        title="Instancia", evaluation_id=evaluation.id, index_in_evaluation=1, instance_weighing=1
    )
    _db.session.add(instance)
    _db.session.commit()

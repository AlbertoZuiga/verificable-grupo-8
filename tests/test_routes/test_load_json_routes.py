import io
import json
from unittest.mock import MagicMock, patch

import pytest
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.datastructures import FileStorage

from app.models.course import Course
from app.models.requisite import Requisite
from app.models.student import Student
from app.models.teacher import Teacher
from app.models.user import User
from app.routes.load_json_routes import process_students_json, process_teachers_json


def test_load_json_index(client):
    response = client.get("/load_json/")
    assert response.status_code == 200
    assert b"Cargar JSON" in response.data


@pytest.mark.parametrize(
    "route, expected_text",
    [
        ("/load_json/students", "Subir Archivo JSON de alumnos"),
        ("/load_json/teachers", "Subir Archivo JSON de profesores"),
        ("/load_json/classrooms", "Subir Archivo JSON de salas"),
        ("/load_json/courses", "Subir Archivo JSON de cursos"),
        ("/load_json/course_instances", "Subir Archivo JSON de instancias de cursos"),
        ("/load_json/sections", "Subir Archivo JSON de secciones"),
        ("/load_json/student_sections", "Subir Archivo JSON de alumnos por sección"),
        ("/load_json/grades", "Subir Archivo JSON de notas"),
    ],
)
def test_load_json_get_routes(client, route, expected_text):
    response = client.get(route)
    assert response.status_code == 200
    assert expected_text.encode("utf-8") in response.data


@patch("app.routes.load_json_routes.process_students_json")
def test_load_students_success(mock_process, client):
    json_data = json.dumps({"alumnos": [{"id": 1, "correo": "test@example.com"}]})
    data = {
        "file": (io.BytesIO(json_data.encode("utf-8")), "students.json"),
        "json_type": "alumnos",
    }
    response = client.post("/load_json/students", data=data, content_type="multipart/form-data")
    assert response.status_code in (302, 200)
    assert mock_process.called


@patch("app.routes.load_json_routes.process_students_json")
def test_load_students_invalid(mock_process, client):
    mock_process.side_effect = ValueError("Invalid data")
    json_data = json.dumps({"alumnos": [{"id": 1, "correo": "test@example.com"}]})
    data = {
        "file": (io.BytesIO(json_data.encode("utf-8")), "students.json"),
        "json_type": "alumnos",
    }

    response = client.post("/load_json/students", data=data, content_type="multipart/form-data")
    assert "Error cargando estudiantes: Invalid data".encode("utf-8") in response.data


@patch("app.routes.load_json_routes.process_teachers_json")
def test_load_teachers_success(mock_process, client):
    json_data = json.dumps({"profesores": [{"id": 1, "correo": "teacher@example.com"}]})
    data = {
        "file": (io.BytesIO(json_data.encode("utf-8")), "teachers.json"),
        "json_type": "profesores",
    }
    response = client.post("/load_json/teachers", data=data, content_type="multipart/form-data")
    assert response.status_code in (302, 200)
    assert mock_process.called


@patch("app.routes.load_json_routes.kanvas_db")
def test_load_classrooms_success(_db, client):
    mock_classroom = MagicMock()
    with patch(
        "app.routes.load_json_routes.parse_classroom_json", return_value=[mock_classroom]
    ), patch(
        "app.routes.load_json_routes.filter_existing_by_field", return_value=[mock_classroom]
    ), patch(
        "app.routes.load_json_routes.add_objects_to_session", return_value=1
    ):

        json_data = json.dumps([{"id": 1, "name": "Aula 1"}])
        data = {
            "file": (io.BytesIO(json_data.encode("utf-8")), "classrooms.json"),
            "json_type": "classrooms",
        }
        response = client.post(
            "/load_json/classrooms", data=data, content_type="multipart/form-data"
        )
        assert response.status_code in (302, 200)


@patch("app.routes.load_json_routes.kanvas_db")
def test_load_courses_success(_db, client):
    mock_course = MagicMock()
    with patch(
        "app.routes.load_json_routes.parse_courses_json", return_value=([mock_course], [])
    ), patch(
        "app.routes.load_json_routes.filter_existing_by_field", return_value=[mock_course]
    ), patch(
        "app.routes.load_json_routes.add_objects_to_session", side_effect=[1, 0]
    ):

        json_data = json.dumps([{"id": 1, "title": "Curso 1"}])
        data = {
            "file": (io.BytesIO(json_data.encode("utf-8")), "courses.json"),
            "json_type": "courses",
        }
        response = client.post("/load_json/courses", data=data, content_type="multipart/form-data")
        assert response.status_code in (302, 200)


@patch("app.routes.load_json_routes.kanvas_db")
def test_load_course_instances_success(_db, client):
    mock_instance = MagicMock()
    with patch(
        "app.routes.load_json_routes.parse_course_instances_json", return_value=[mock_instance]
    ), patch(
        "app.routes.load_json_routes.filter_existing_by_field", return_value=[mock_instance]
    ), patch(
        "app.routes.load_json_routes.add_objects_to_session", return_value=1
    ):

        json_data = json.dumps([{"id": 1, "year": 2023}])
        data = {
            "file": (io.BytesIO(json_data.encode("utf-8")), "instances.json"),
            "json_type": "course_instances",
        }
        response = client.post(
            "/load_json/course_instances", data=data, content_type="multipart/form-data"
        )
        assert response.status_code in (302, 200)


@patch("app.routes.load_json_routes.kanvas_db")
def test_load_sections_success(_db, client):
    with patch(
        "app.routes.load_json_routes.parse_sections_json",
        return_value=([MagicMock()], [MagicMock()], [MagicMock()]),
    ), patch(
        "app.routes.load_json_routes.filter_existing_by_field", return_value=[MagicMock()]
    ), patch(
        "app.routes.load_json_routes.add_objects_to_session", side_effect=[1, 1, 1]
    ):

        json_data = json.dumps([{"id": 1, "code": "SEC-001"}])
        data = {
            "file": (io.BytesIO(json_data.encode("utf-8")), "sections.json"),
            "json_type": "sections",
        }
        response = client.post("/load_json/sections", data=data, content_type="multipart/form-data")
        assert response.status_code in (302, 200)


@patch("app.routes.load_json_routes.kanvas_db")
def test_load_student_sections_success(_db, client):
    mock_link = MagicMock()
    with patch(
        "app.routes.load_json_routes.parse_student_sections_json", return_value=[mock_link]
    ), patch(
        "app.routes.load_json_routes.filter_existing_by_two_fields", return_value=[mock_link]
    ), patch(
        "app.routes.load_json_routes.add_objects_to_session", return_value=1
    ):

        json_data = json.dumps([{"student_id": 1, "section_id": 1}])
        data = {
            "file": (io.BytesIO(json_data.encode("utf-8")), "student_sections.json"),
            "json_type": "student_sections",
        }
        response = client.post(
            "/load_json/student_sections", data=data, content_type="multipart/form-data"
        )
        assert response.status_code in (302, 200)


@patch("app.routes.load_json_routes.kanvas_db")
def test_load_grades_success(_db, client):
    mock_grade = MagicMock()
    with patch("app.routes.load_json_routes.parse_grades_json", return_value=[mock_grade]), patch(
        "app.routes.load_json_routes.filter_grades", return_value=[mock_grade]
    ), patch("app.routes.load_json_routes.add_objects_to_session", return_value=1):

        json_data = json.dumps([{"student_id": 1, "evaluation_instance_id": 1}])
        data = {
            "file": (io.BytesIO(json_data.encode("utf-8")), "grades.json"),
            "json_type": "grades",
        }
        response = client.post("/load_json/grades", data=data, content_type="multipart/form-data")
        assert response.status_code in (302, 200)


# Tests para manejo de errores
@pytest.mark.parametrize(
    "route",
    [
        "/load_json/students",
        "/load_json/teachers",
        "/load_json/classrooms",
        "/load_json/courses",
        "/load_json/course_instances",
        "/load_json/sections",
        "/load_json/student_sections",
        "/load_json/grades",
    ],
)
def test_load_routes_invalid_file(client, route):
    data = {"file": (io.BytesIO(b""), "empty.json"), "json_type": route.split("/")[-1]}
    response = client.post(route, data=data, content_type="multipart/form-data")
    assert response.status_code == 200
    assert (
        b"Selecciona un archivo JSON" in response.data
        or b"Este campo es obligatorio" in response.data
    )


@pytest.mark.parametrize(
    "route",
    [
        "/load_json/students",
        "/load_json/teachers",
        "/load_json/classrooms",
        "/load_json/courses",
        "/load_json/course_instances",
        "/load_json/sections",
        "/load_json/student_sections",
        "/load_json/grades",
    ],
)
def test_load_routes_invalid_json_type(client, route):
    json_type = "invalid_type"
    json_data = json.dumps({})
    data = {
        "file": (io.BytesIO(json_data.encode("utf-8")), "test.json"),
        "json_type": json_type,
    }
    response = client.post(route, data=data, content_type="multipart/form-data")
    assert response.status_code == 200
    assert "Tipo de JSON inválido".encode("utf-8") in response.data


# Prueba para JSON mal formado
def test_load_students_malformed_json(client):
    data = {
        "file": (io.BytesIO(b"{invalid json}"), "malformed.json"),
        "json_type": "alumnos",
    }

    response = client.post("/load_json/students", data=data, content_type="multipart/form-data")

    assert response.status_code == 200
    assert "El contenido del archivo no es un JSON válido.".encode("utf-8") in response.data


def test_load_students_missing_fields(client):
    json_data = json.dumps({"alumnos": [{"id": 1}]})  # Falta correo y nombre
    data = {
        "file": (io.BytesIO(json_data.encode("utf-8")), "missing_fields.json"),
        "json_type": "alumnos",
    }
    response = client.post("/load_json/students", data=data, content_type="multipart/form-data")

    assert response.status_code == 200
    assert b"Error cargando estudiantes:" in response.data


def test_process_students_json(client, _db):
    with client.application.test_request_context():
        json_data = json.dumps(
            {
                "alumnos": [
                    {
                        "id": 100,
                        "nombre": "John Doe",
                        "correo": "john.doe@example.com",
                        "anio_ingreso": 2023,
                    }
                ]
            }
        ).encode("utf-8")

        file = FileStorage(stream=io.BytesIO(json_data), filename="students.json")
        process_students_json(file)

        student = Student.query.get(100)
        assert student is not None
        assert student.user.email == "john.doe@example.com"


def test_process_teachers_json(client, _db):
    with client.application.test_request_context():
        json_data = json.dumps(
            {
                "profesores": [
                    {
                        "id": 200,
                        "nombre": "Jane Smith",
                        "correo": "jane.smith@example.com",
                    }
                ]
            }
        ).encode("utf-8")

        file = FileStorage(stream=io.BytesIO(json_data), filename="teachers.json")
        process_teachers_json(file)

        teacher = Teacher.query.get(200)
        assert teacher is not None
        assert teacher.user.email == "jane.smith@example.com"


# Prueba para verificar manejo de errores en procesamiento
def test_process_students_json_invalid(_db):
    with pytest.raises(ValueError):
        file = FileStorage(stream=io.BytesIO(b'{"invalid": []}'), filename="students.json")
        process_students_json(file)


def test_load_empty_file(client):
    data = {
        "file": (io.BytesIO(b""), "empty.json"),
        "json_type": "alumnos",
    }
    response = client.post("/load_json/students", data=data, content_type="multipart/form-data")
    assert "El archivo está vacío".encode("utf-8") in response.data


# Prueba para datos duplicados
def test_load_duplicate_data(_db, client):
    user = User(email="existing@example.com", first_name="John", last_name="Doe")
    user.set_password("password")
    _db.session.add(user)
    _db.session.commit()

    json_data = json.dumps(
        {
            "alumnos": [
                {
                    "id": 1,
                    "nombre": "John",
                    "apellido": "Doe",
                    "correo": "existing@example.com",
                    "anio_ingreso": 2023,
                }
            ]
        }
    )
    data = {
        "file": (io.BytesIO(json_data.encode("utf-8")), "duplicate.json"),
        "json_type": "alumnos",
    }
    response = client.post("/load_json/students", data=data, content_type="multipart/form-data")
    assert response.status_code == 200
    assert b"Error cargando estudiantes: Ya existe un usuario con el correo" in response.data


def test_load_students_database_error(client, monkeypatch):
    def mock_commit():
        raise SQLAlchemyError("Error de base de datos")

    monkeypatch.setattr("app.routes.load_json_routes.kanvas_db.session.commit", mock_commit)

    json_data = json.dumps(
        {
            "alumnos": [
                {
                    "id": 1,
                    "nombre": "John",
                    "apellido": "Doe",
                    "correo": "test@example.com",
                    "anio_ingreso": 2023,
                }
            ]
        }
    )
    data = {
        "file": (io.BytesIO(json_data.encode("utf-8")), "students.json"),
        "json_type": "alumnos",
    }
    response = client.post("/load_json/students", data=data, content_type="multipart/form-data")
    assert b"Error cargando estudiantes: " in response.data


# Pruebas para carga de requisitos
def test_load_courses_with_requisites(_db, client):
    json_data = json.dumps(
        {
            "cursos": [
                {
                    "id": 1,
                    "codigo": "CR-101",
                    "descripcion": "Curso sin Requisitos",
                    "requisitos": [],
                    "creditos": 4,
                },
                {
                    "id": 2,
                    "codigo": "CR-102",
                    "descripcion": "Curso con Requisito",
                    "requisitos": ["CR-101"],
                    "creditos": 2,
                },
                {
                    "id": 3,
                    "codigo": "CR-103",
                    "descripcion": "Curso con Requisitos",
                    "requisitos": ["CR-101", "CR-102"],
                    "creditos": 2,
                },
            ]
        }
    )
    data = {
        "file": (io.BytesIO(json_data.encode("utf-8")), "courses.json"),
        "json_type": "cursos",
    }
    response = client.post(
        "/load_json/courses", data=data, content_type="multipart/form-data", follow_redirects=True
    )
    assert response.status_code == 200
    assert Requisite.query.count() == 3
    assert Course.query.count() == 3


def test_load_invalid_grades(_db, client):
    json_data = json.dumps(
        {"notas": [{"alumno_id": 999, "topico_id": 999, "instancia": 1, "nota": 7.0}]}
    )
    data = {
        "file": (io.BytesIO(json_data.encode("utf-8")), "grades.json"),
        "json_type": "notas",
    }
    response = client.post("/load_json/grades", data=data, content_type="multipart/form-data")
    assert "No existe un estudiante con ID".encode("utf-8") in response.data

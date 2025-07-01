import io
import json
from unittest.mock import MagicMock, patch

import pytest
from werkzeug.datastructures import FileStorage

from app.models.course import Course
from app.models.requisite import Requisite
from app.models.student import Student
from app.models.teacher import Teacher
from app.models.user import User
from app.routes.load_json_routes import process_students_json, process_teachers_json

# 1. Tests para rutas GET -----------------------------------------------------


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


# 2. Tests para rutas POST exitosas --------------------------------------------


@pytest.mark.parametrize(
    "route, json_type, mock_target, return_value",
    [
        ("/load_json/students", "alumnos", "process_students_json", None),
        ("/load_json/teachers", "profesores", "process_teachers_json", None),
        ("/load_json/classrooms", "salas", "parse_classrooms_json", [MagicMock()]),
        ("/load_json/courses", "cursos", "parse_courses_json", ([MagicMock()], [])),
        ("/load_json/course_instances", "instancias", "parse_course_instances_json", [MagicMock()]),
        (
            "/load_json/sections",
            "secciones",
            "parse_sections_json",
            ([MagicMock()], [MagicMock()], [MagicMock()]),
        ),
        (
            "/load_json/student_sections",
            "alumnos_seccion",
            "parse_student_sections_json",
            [MagicMock()],
        ),
        ("/load_json/grades", "notas", "parse_grades_json", [MagicMock()]),
    ],
)
def test_load_routes_success(client, route, json_type, mock_target, return_value):
    # Datos comunes para todas las rutas
    json_data = json.dumps({})
    filename = route.split("/")[-1] + ".json"

    # Configuración de mocks específica
    with patch(
        f"app.routes.load_json_routes.{mock_target}", return_value=return_value
    ) as mock_func:
        # Configuración adicional para rutas que necesitan múltiples mocks
        if route == "/load_json/classrooms":
            with patch(
                "app.routes.load_json_routes.filter_existing_by_field", return_value=return_value
            ), patch("app.routes.load_json_routes.add_objects_to_session", return_value=1):
                response = post_request(client, route, json_type, json_data, filename)

        elif route == "/load_json/courses":
            with patch(
                "app.routes.load_json_routes.filter_existing_by_field", return_value=return_value[0]
            ), patch("app.routes.load_json_routes.add_objects_to_session", side_effect=[1, 0]):
                response = post_request(client, route, json_type, json_data, filename)

        elif route == "/load_json/sections":
            with patch(
                "app.routes.load_json_routes.filter_existing_by_field", return_value=return_value[0]
            ), patch("app.routes.load_json_routes.add_objects_to_session", side_effect=[1, 1, 1]):
                response = post_request(client, route, json_type, json_data, filename)

        elif route in ("/load_json/student_sections", "/load_json/grades"):
            filter_func = (
                "filter_existing_by_two_fields" if "student_sections" in route else "filter_grades"
            )
            with patch(
                f"app.routes.load_json_routes.{filter_func}", return_value=return_value
            ), patch("app.routes.load_json_routes.add_objects_to_session", return_value=1):
                response = post_request(client, route, json_type, json_data, filename)

        else:
            response = post_request(client, route, json_type, json_data, filename)

        assert response.status_code in (200, 302)
        assert mock_func.called


def post_request(client, route, json_type, json_data, filename):
    data = {
        "file": (io.BytesIO(json_data.encode("utf-8")), filename),
        "json_type": json_type,
    }
    return client.post(route, data=data, content_type="multipart/form-data")


# 3. Tests para casos de error -------------------------------------------------


@pytest.mark.parametrize(
    "route, error_type, error_message, json_type",
    [
        ("/load_json/students", "ValueError", "Invalid data", "alumnos"),
        ("/load_json/teachers", "SQLAlchemyError", "Falta la clave", "profesores"),
        ("/load_json/classrooms", "ValueError", "Parsing error", "salas"),
        ("/load_json/courses", "SQLAlchemyError", "Falta la clave", "cursos"),
        ("/load_json/course_instances", "ValueError", "Invalid format", "instancias"),
        ("/load_json/sections", "SQLAlchemyError", "Falta la clave", "secciones"),
        ("/load_json/student_sections", "ValueError", "Missing fields", "alumnos_seccion"),
        ("/load_json/grades", "SQLAlchemyError", "Falta la clave", "notas"),
    ],
)
def test_load_routes_error_handling(
    client, route, error_type, error_message, json_type, monkeypatch
):
    # Configuración de mocks para simular errores
    if error_type == "ValueError":
        if "students" in route or "teachers" in route:
            monkeypatch.setattr(
                f"app.routes.load_json_routes.{
                    'process_students_json' if 'students' in route else 'process_teachers_json'
                }",
                lambda x: exec('raise ValueError("' + error_message + '")'),
            )
        else:
            target = route.split("/")[-1].replace("-", "_")
            monkeypatch.setattr(
                f"app.routes.load_json_routes.parse_{target}_json",
                lambda x: exec('raise ValueError("' + error_message + '")'),
            )
    else:  # SQLAlchemyError
        monkeypatch.setattr(
            "app.routes.load_json_routes.kanvas_db.session.commit",
            lambda: exec('raise SQLAlchemyError("' + error_message + '")'),
        )

    # Datos de prueba
    json_data = json.dumps({"dummy": 1})
    filename = route.split("/")[-1] + ".json"
    data = {
        "file": (io.BytesIO(json_data.encode("utf-8")), filename),
        "json_type": json_type,
    }

    response = client.post(route, data=data, content_type="multipart/form-data")
    print("Response:\n", response.data.decode())
    assert response.status_code == 200
    assert error_message.encode("utf-8") in response.data


# Lista de rutas y tipos de JSON válidos
ROUTES_AND_TYPES = [
    ("/load_json/students", "alumnos"),
    ("/load_json/teachers", "profesores"),
    ("/load_json/classrooms", "salas"),
    ("/load_json/courses", "cursos"),
    ("/load_json/course_instances", "instancias"),
    ("/load_json/sections", "secciones"),
    ("/load_json/student_sections", "alumnos_seccion"),
    ("/load_json/grades", "notas"),
]

# Escenarios de prueba
SCENARIOS = [
    "empty_file",
    "invalid_json_type",
    "malformed_json",
    "missing_fields",
]


# Parametrizamos todas las combinaciones posibles
@pytest.mark.parametrize("route,json_type", ROUTES_AND_TYPES)
@pytest.mark.parametrize("scenario", SCENARIOS)
def test_load_routes_common_errors(client, route, json_type, scenario):
    if scenario == "empty_file":
        data = {"file": (io.BytesIO(b""), "empty.json"), "json_type": json_type}
        expected_error = b"El archivo est"
    elif scenario == "invalid_json_type":
        data = {
            "file": (io.BytesIO(b"{}"), "test.json"),
            "json_type": "invalid_type",
        }
        expected_error = b"Tipo de JSON inv"
    elif scenario == "malformed_json":
        data = {
            "file": (io.BytesIO(b"{invalid}"), "malformed.json"),
            "json_type": json_type,
        }
        expected_error = b"El contenido del archivo no es un JSON v"
    elif scenario == "missing_fields":
        json_data = json.dumps([{}])
        data = {
            "file": (io.BytesIO(json_data.encode("utf-8")), "missing.json"),
            "json_type": json_type,
        }
        expected_error = b"El archivo JSON debe tener un objeto como estructura principal."
    else:
        pytest.fail(f"Escenario no soportado: {scenario}")
        raise ValueError(f"Escenario desconocido: {scenario}")

    response = client.post(route, data=data, content_type="multipart/form-data")
    assert response.status_code == 200
    assert expected_error in response.data


# 4. Tests para funciones de procesamiento -------------------------------------


@pytest.mark.parametrize(
    "json_data, expected_count, entity_type",
    [
        (
            {
                "alumnos": [
                    {
                        "id": 100,
                        "nombre": "John",
                        "apellido": "Doe",
                        "correo": "john.doe@example.com",
                        "anio_ingreso": 2023,
                    }
                ]
            },
            1,
            "student",
        ),
        (
            {
                "profesores": [
                    {
                        "id": 200,
                        "nombre": "Jane",
                        "apellido": "Smith",
                        "correo": "jane.smith@example.com",
                    }
                ]
            },
            1,
            "teacher",
        ),
        (
            {
                "alumnos": [
                    {
                        "id": 101,
                        "nombre": "A",
                        "apellido": "B",
                        "correo": "a@b.com",
                        "anio_ingreso": 2023,
                    },
                    {
                        "id": 102,
                        "nombre": "C",
                        "apellido": "D",
                        "correo": "c@d.com",
                        "anio_ingreso": 2023,
                    },
                ]
            },
            2,
            "student",
        ),
    ],
)
def test_process_json_success(client, _db, json_data, expected_count, entity_type):
    with client.application.test_request_context():
        # Preparar datos
        file_content = json.dumps(json_data).encode("utf-8")
        filename = "students.json" if entity_type == "student" else "teachers.json"
        file = FileStorage(stream=io.BytesIO(file_content), filename=filename)

        # Ejecutar función
        if entity_type == "student":
            process_students_json(file)
            entity = Student.query.get(100 if expected_count == 1 else 101)
        else:
            process_teachers_json(file)
            entity = Teacher.query.get(200)

        # Verificar resultados
        assert entity is not None
        if entity_type == "student":
            assert Student.query.count() == expected_count
            assert entity.user.email in ["john.doe@example.com", "a@b.com"]
        else:
            assert Teacher.query.count() == expected_count
            assert entity.user.email == "jane.smith@example.com"


@pytest.mark.parametrize(
    "json_data, expected_error, entity_type",
    [
        (b'{"invalid": []}', "Falta la clave", "student"),
        (b'{"profesores": [{"id": 1}]}', "Falta la clave", "teacher"),
        (b'{"alumnos": [{"id": 1, "nombre": "A"}]}', "Falta la clave", "student"),
    ],
)
def test_process_json_invalid(_db, json_data, expected_error, entity_type):
    file = FileStorage(
        stream=io.BytesIO(json_data),
        filename="students.json" if entity_type == "student" else "teachers.json",
    )

    with pytest.raises(ValueError) as excinfo:
        if entity_type == "student":
            process_students_json(file)
        else:
            process_teachers_json(file)

    assert expected_error in str(excinfo.value)


# 5. Tests para casos específicos de integración -------------------------------


@pytest.mark.parametrize(
    "scenario, expected_requisites, expected_courses",
    [
        ("without_requisites", 0, 1),
        ("with_requisites", 3, 3),
    ],
)
def test_load_courses_with_requisites(_db, client, scenario, expected_requisites, expected_courses):
    # Preparar datos según el escenario
    if scenario == "with_requisites":
        json_data = {
            "cursos": [
                {
                    "id": 1,
                    "codigo": "CR-101",
                    "descripcion": "Curso 1",
                    "requisitos": [],
                    "creditos": 4,
                },
                {
                    "id": 2,
                    "codigo": "CR-102",
                    "descripcion": "Curso 2",
                    "requisitos": ["CR-101"],
                    "creditos": 2,
                },
                {
                    "id": 3,
                    "codigo": "CR-103",
                    "descripcion": "Curso 3",
                    "requisitos": ["CR-101", "CR-102"],
                    "creditos": 2,
                },
            ]
        }
    else:
        json_data = {
            "cursos": [
                {
                    "id": 1,
                    "codigo": "CR-101",
                    "descripcion": "Curso 1",
                    "requisitos": [],
                    "creditos": 4,
                },
            ]
        }

    data = {
        "file": (io.BytesIO(json.dumps(json_data).encode("utf-8")), "courses.json"),
        "json_type": "cursos",
    }

    response = client.post(
        "/load_json/courses", data=data, content_type="multipart/form-data", follow_redirects=True
    )

    assert response.status_code == 200
    assert Requisite.query.count() == expected_requisites
    assert Course.query.count() == expected_courses


@pytest.mark.parametrize(
    "scenario",
    [
        "invalid_student",
        "invalid_evaluation",
        "invalid_section",
    ],
)
def test_load_invalid_grades(_db, client, scenario):
    # Crear datos válidos si son necesarios
    if scenario != "invalid_student":
        user = User(email="test@example.com", first_name="Test", last_name="User")
        user.set_password("password")
        _db.session.add(user)
        _db.session.commit()
        student = Student(user_id=user.id, university_entry_year=2023)
        _db.session.add(student)
        _db.session.commit()
        student_id = student.id
    else:
        student_id = 9999

    # Preparar datos según el escenario
    if scenario == "invalid_evaluation":
        evaluation_id = 9999
    else:
        evaluation_id = 1

    json_data = {
        "notas": [
            {"alumno_id": student_id, "topico_id": evaluation_id, "instancia": 1, "nota": 7.0}
        ]
    }

    data = {
        "file": (io.BytesIO(json.dumps(json_data).encode("utf-8")), "grades.json"),
        "json_type": "notas",
    }

    response = client.post("/load_json/grades", data=data, content_type="multipart/form-data")
    assert b"No existe un" in response.data

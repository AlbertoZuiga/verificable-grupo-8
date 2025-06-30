import pytest
from flask import url_for

from app.extensions import kanvas_db
from app.models.evaluation import Evaluation
from app.models.section import Section, WeighingType
from app.models.section_grade import SectionGrade
from app.models.student_evaluation_instance import StudentEvaluationInstance


# ---------------------------
# Pruebas para index()
# ---------------------------
def test_index(client, test_open_section, test_closed_section):
    response = client.get(url_for("section.index"))
    assert response.status_code == 200
    assert str(test_open_section.code).encode() in response.data
    assert str(test_closed_section.code).encode() in response.data


# ---------------------------
# Pruebas para show()
# ---------------------------
def test_show_success(client, test_open_section):
    response = client.get(url_for("section.show", section_id=test_open_section.id))
    assert response.status_code == 200
    assert str(test_open_section.code).encode() in response.data


def test_show_not_found(client, _db):
    response = client.get(url_for("section.show", section_id=9999))
    assert response.status_code == 404


# ---------------------------
# Pruebas para create()
# ---------------------------
def test_create_section_success(client, test_course_instance, test_teacher):
    with client:
        data = {
            "course_instance_id": test_course_instance.id,
            "teacher_id": test_teacher.id,
            "code": "1234",
            "weighing_type": WeighingType.WEIGHT.name,
        }

        response = client.post(url_for("section.create"), data=data, follow_redirects=True)
        assert response.status_code == 200
        assert "Sección creada exitosamente".encode("utf-8") in response.data

        section = Section.query.filter_by(code="1234").first()
        assert section is not None


@pytest.mark.parametrize(
    "form_data, expected_error",
    [
        # Curso vacío
        (
            {
                "course_instance_id": "",
                "teacher_id": 1,
                "code": 1234,
                "weighing_type": WeighingType.WEIGHT.name,
            },
            b"Instancia de curso debe estar presente.",
        ),
        # Curso inválido (ID no permitido por AnyOf)
        (
            {
                "course_instance_id": 9999,
                "teacher_id": 1,
                "code": 1234,
                "weighing_type": WeighingType.WEIGHT.name,
            },
            b"Debes seleccionar una instancia de curso valida.",
        ),
        # Profesor vacío
        (
            {
                "course_instance_id": 1,
                "teacher_id": "",
                "code": 1234,
                "weighing_type": WeighingType.WEIGHT.name,
            },
            b"Profesor debe estar presente.",
        ),
        # Profesor inválido
        (
            {
                "course_instance_id": 1,
                "teacher_id": 9999,
                "code": 1234,
                "weighing_type": WeighingType.WEIGHT.name,
            },
            b"Debes seleccionar una profesor valido.",
        ),
        # Código vacío
        (
            {
                "course_instance_id": 1,
                "teacher_id": 1,
                "code": "",
                "weighing_type": WeighingType.WEIGHT.name,
            },
            b"Codigo debe estar presente.",
        ),
        # Código fuera de rango
        (
            {
                "course_instance_id": 1,
                "teacher_id": 1,
                "code": -3,
                "weighing_type": WeighingType.WEIGHT.name,
            },
            b"Debe ser un numero entre 1 y 5000.",
        ),
        # Tipo de ponderación vacío
        (
            {
                "course_instance_id": 1,
                "teacher_id": 1,
                "code": 1234,
                "weighing_type": "",
            },
            b"Tipo de ponderacion debe estar presente.",
        ),
    ],
)
def test_create_section_invalid_inputs(
    client,
    test_course_instance,
    test_teacher,
    form_data,
    expected_error
):
    form_data["course_instance_id"] = form_data.get("course_instance_id", test_course_instance.id)
    form_data["teacher_id"] = form_data.get("teacher_id", test_teacher.id)

    response = client.post(url_for("section.create"), data=form_data)
    assert expected_error in response.data


# ---------------------------
# Pruebas para edit()
# ---------------------------
def test_edit_section_success(client, test_open_section, test_course_instance, test_teacher):
    data = {
        "course_instance_id": test_course_instance.id,
        "teacher_id": test_teacher.id,
        "code": "1234",
        "weighing_type": WeighingType.PERCENTAGE.name,
    }

    response = client.post(
        url_for("section.edit", section_id=test_open_section.id), data=data, follow_redirects=True
    )
    assert response.status_code == 200
    assert "Sección actualizada exitosamente".encode("utf-8") not in response.data

    # Verificar cambios en la base de datos
    updated_section = Section.query.get(test_open_section.id)
    assert updated_section.code == 1234
    assert updated_section.weighing_type == WeighingType.PERCENTAGE


def test_edit_closed_section(client, test_closed_section):
    response = client.get(
        url_for("section.edit", section_id=test_closed_section.id), follow_redirects=True
    )
    assert "Esta sección está cerrada y no puede ser modificada.".encode("utf-8") in response.data
    assert response.status_code == 200


# ---------------------------
# Pruebas para delete()
# ---------------------------
def test_delete_section_success(client, test_open_section, app):
    section_id = test_open_section.id
    response = client.post(url_for("section.delete", section_id=section_id), follow_redirects=True)
    assert response.status_code == 200
    assert "Sección eliminada con éxito".encode("utf-8") in response.data

    with app.app_context():
        assert Section.query.get(section_id) is None


def test_delete_closed_section(client, test_closed_section):
    response = client.post(
        url_for("section.delete", section_id=test_closed_section.id), follow_redirects=True
    )
    assert "Esta sección está cerrada y no puede ser modificada.".encode("utf-8") in response.data
    assert response.status_code == 200


# ---------------------------
# Pruebas para edit_evaluation_weights()
# ---------------------------
def test_edit_weights_success(client, test_open_section, _test_evaluation):
    data = {f"evaluation_{_test_evaluation.id}": 50.0}

    response = client.post(
        url_for("section.edit_evaluation_weights", section_id=test_open_section.id),
        data=data,
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Pesos de evaluaciones actualizados correctamente" in response.data

    # Verificar cambio en la base de datos
    updated_evaluation = Evaluation.query.get(_test_evaluation.id)
    assert abs(updated_evaluation.weighing - 50.0) < 1e-6


def test_edit_weights_invalid_input(client, test_open_section):
    data = {"evaluation_999": "invalid"}

    response = client.post(
        url_for("section.edit_evaluation_weights", section_id=test_open_section.id),
        data=data,
        follow_redirects=True,
    )

    assert "Entrada inválida para los pesos".encode("utf-8") in response.data


def test_edit_weights_percentage_invalid(client, test_open_section, _test_evaluation):
    # Cambiar a tipo porcentaje
    test_open_section.weighing_type = WeighingType.PERCENTAGE
    kanvas_db.session.commit()

    data = {f"evaluation_{_test_evaluation.id}": 50.0}  # Suma != 100

    response = client.post(
        url_for("section.edit_evaluation_weights", section_id=test_open_section.id),
        data=data,
        follow_redirects=True,
    )
    assert b"debe ser 100 para las evaluaciones ponderadas" in response.data


# ---------------------------
# Pruebas para close()
# ---------------------------
def test_close_section_success(
    client,
    test_open_section,
    _test_evaluation,
    test_evaluation_instance,
    _test_student_in_section,
):
    with client:
        # Crear calificación para el estudiante
        grade = StudentEvaluationInstance(
            student_id=_test_student_in_section.student.id,
            evaluation_instance_id=test_evaluation_instance.id,
            grade=7.0,
        )
        kanvas_db.session.add(grade)
        kanvas_db.session.commit()

        response = client.post(
            url_for("section.close", section_id=test_open_section.id), follow_redirects=True
        )
        assert response.status_code == 200
        assert "La sección fue cerrada exitosamente".encode("utf-8") in response.data

        # Verificar que la sección se cerró
        section = Section.query.get(test_open_section.id)
        assert section.closed is True

        # Verificar nota final
        section_grade = SectionGrade.query.filter_by(
            section_id=section.id, student_id=_test_student_in_section.student.id
        ).first()
        assert section_grade is not None
        assert abs(section_grade.grade - 7.0) < 1e-6


# ---------------------------
# Pruebas para grades()
# ---------------------------
def test_grades_success(client, test_closed_section, test_student_in_closed_section):
    # Crear nota final
    grade = SectionGrade(
        student_id=test_student_in_closed_section.student.id,
        section_id=test_closed_section.id,
        grade=5.5,
    )
    kanvas_db.session.add(grade)
    kanvas_db.session.commit()

    response = client.get(url_for("section.grades", section_id=test_closed_section.id))
    assert response.status_code == 200
    assert b"5.5" in response.data  # Verificar que se muestra la nota

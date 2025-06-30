from unittest.mock import patch

from flask import url_for
from sqlalchemy.exc import SQLAlchemyError

from app.models.student_evaluation_instance import StudentEvaluationInstance



def test_assign_new_grade_success(
    client, test_student_in_section, test_evaluation_instance
):
    url = url_for(
        "grades.assign_or_edit_grade",
        evaluation_instance_id=test_evaluation_instance.id,
        student_id=test_student_in_section.student.id,
    )

    response = client.post(url, data={"grade": "8.5"})

    assert response.status_code == 302
    grade = StudentEvaluationInstance.query.filter_by(
        evaluation_instance_id=test_evaluation_instance.id,
        student_id=test_student_in_section.student.id,
    ).first()
    assert grade is not None
    assert abs(grade.grade - 8.5) < 1e-6

def test_update_existing_grade(client, test_grade, test_student_in_section):
    url = url_for(
        "grades.assign_or_edit_grade",
        evaluation_instance_id=test_grade.evaluation_instance_id,
        student_id=test_grade.student_id,
    )

    response = client.post(url, data={"grade": "9.0"})

    assert response.status_code == 302
    updated_grade = StudentEvaluationInstance.query.filter_by(
        evaluation_instance_id=test_grade.evaluation_instance_id,
        student_id=test_grade.student_id,
    ).first()
    assert abs(updated_grade.grade - 9.0) < 1e-6

def test_assign_grade_closed_section(
    client, test_evaluation_instance_closed_section, test_student_in_closed_section
):
    with client:
        url = url_for(
            "grades.assign_or_edit_grade",
            evaluation_instance_id=test_evaluation_instance_closed_section.id,
            student_id=test_student_in_closed_section.student.id,
        )

        response = client.get(url)

        assert response.status_code == 302
        assert response.headers["Location"].endswith(
            url_for(
                "evaluation_instance.show",
                evaluation_instance_id=test_evaluation_instance_closed_section.id,
                _external=False,
            )
        )

def test_assign_grade_invalid_student(
    client, test_evaluation_instance, test_student_not_in_section
):
    url = url_for(
        "grades.assign_or_edit_grade",
        evaluation_instance_id=test_evaluation_instance.id,
        student_id=test_student_not_in_section.id,
    )

    response = client.get(url)

    assert response.status_code == 404
    assert "Estudiante no pertenece" in response.data.decode()

def test_assign_grade_invalid_input(
    client, test_student_in_section, test_evaluation_instance
):
    url = url_for(
        "grades.assign_or_edit_grade",
        evaluation_instance_id=test_evaluation_instance.id,
        student_id=test_student_in_section.student.id,
    )

    response_empty = client.post(url, data={"grade": ""})
    assert response_empty.status_code == 400

    response_invalid = client.post(url, data={"grade": "A+"})
    assert response_invalid.status_code == 400

@patch("app.routes.grade_routes._save_grade_transaction")
def test_grade_transaction_error(
    mock_save, client, test_student_in_section, test_evaluation_instance
):
    mock_save.side_effect = SQLAlchemyError("DB error")

    url = url_for(
        "grades.assign_or_edit_grade",
        evaluation_instance_id=test_evaluation_instance.id,
        student_id=test_student_in_section.student.id,
    )

    response = client.post(url, data={"grade": "7.5"})

    assert response.status_code == 500
    assert "Error al guardar la nota" in response.data.decode()


def test_delete_grade_success(client, test_grade):
    url = url_for(
        "grades.delete_grade",
        evaluation_instance_id=test_grade.evaluation_instance_id,
        student_id=test_grade.student_id,
    )

    response = client.post(url)

    assert response.status_code == 302
    deleted_grade = StudentEvaluationInstance.query.filter_by(
        evaluation_instance_id=test_grade.evaluation_instance_id,
        student_id=test_grade.student_id,
    ).first()
    assert deleted_grade is None

def test_delete_nonexistent_grade(client, test_evaluation_instance, test_student):
    url = url_for(
        "grades.delete_grade",
        evaluation_instance_id=test_evaluation_instance.id,
        student_id=test_student.id,
    )

    response = client.post(url)

    assert response.status_code == 404
    assert "Nota no encontrada" in response.data.decode()

@patch("app.routes.grade_routes.kanvas_db.session.commit")
def test_delete_grade_db_error(mock_commit, client, test_grade):
    mock_commit.side_effect = SQLAlchemyError("DB error")

    url = url_for(
        "grades.delete_grade",
        evaluation_instance_id=test_grade.evaluation_instance_id,
        student_id=test_grade.student_id,
    )

    response = client.post(url)

    assert response.status_code == 500
    assert "Error al eliminar la nota" in response.data.decode()

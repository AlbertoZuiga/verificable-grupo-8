from flask import get_flashed_messages, url_for
from sqlalchemy.exc import SQLAlchemyError

from app.models.requisite import Requisite


# Pruebas para la ruta de creación de requisitos
def test_create_requisite_success(client, test_course, test_course2):
    data = {
        "course_id": test_course.id,
        "requisite_id": test_course2.id,
    }
    response = client.post(url_for("requisite.create"), data=data)

    assert response.status_code == 302
    assert response.location.endswith(
        url_for("course.show", course_id=test_course.id, _external=False)
    )

    # Verificar que se creó el requisito en la base de datos
    requisite = Requisite.query.filter_by(
        course_id=test_course.id, course_requisite_id=test_course2.id
    ).first()
    assert requisite is not None


def test_create_requisite_missing_data(client, test_course, _db):
    with client:
        # Falta requisite_id
        data = {"course_id": test_course.id}
        response = client.post(url_for("requisite.create"), data=data)

        assert response.status_code == 302
        assert response.location.endswith(
            url_for("course.show", course_id=test_course.id, _external=False)
        )

        # Verificar mensaje flash
        messages = get_flashed_messages(with_categories=True)
        assert ("danger", "Debe seleccionar un curso y su requisito.") in messages


def test_create_requisite_inverse_exists(client, test_course, test_course2, _db):
    with client:
        inverse = Requisite(course_id=test_course2.id, course_requisite_id=test_course.id)
        _db.session.add(inverse)
        _db.session.commit()

        data = {
            "course_id": test_course.id,
            "requisite_id": test_course2.id,
        }
        response = client.post(url_for("requisite.create"), data=data)

        assert response.status_code == 302
        assert response.location.endswith(
            url_for("course.show", course_id=test_course.id, _external=False)
        )

        # Verificar mensaje flash
        messages = get_flashed_messages(with_categories=True)
        expected_msg = "No se puede asignar como requisito un curso que depende del curso actual."
        assert ("danger", expected_msg) in messages

        # Verificar que no se creó el nuevo requisito
        requisite = Requisite.query.filter_by(
            course_id=test_course.id, course_requisite_id=test_course2.id
        ).first()
        assert requisite is None


def test_create_requisite_cyclic_dependency(client, test_course, test_course2, test_course3, _db):
    with client:
        # Crear cadena de requisitos: test_course -> test_course2
        req1 = Requisite(course_id=test_course.id, course_requisite_id=test_course2.id)
        _db.session.add(req1)

        # Crear cadena: test_course2 -> test_course3
        req2 = Requisite(course_id=test_course2.id, course_requisite_id=test_course3.id)
        _db.session.add(req2)

        _db.session.commit()

        # Intentar crear ciclo: test_course3 -> test_course
        data = {
            "course_id": test_course3.id,
            "requisite_id": test_course.id,
        }
        response = client.post(url_for("requisite.create"), data=data)

        assert response.status_code == 302
        assert response.location.endswith(
            url_for("course.show", course_id=test_course3.id, _external=False)
        )

        # Verificar mensaje flash
        messages = get_flashed_messages(with_categories=True)
        expected_msg = "No se puede asignar como requisito un curso que depende del curso actual."
        assert ("danger", expected_msg) in messages

        # Verificar que no se creó el requisito
        requisite = Requisite.query.filter_by(
            course_id=test_course3.id, course_requisite_id=test_course.id
        ).first()
        assert requisite is None


# Pruebas para la ruta de eliminación de requisitos
def test_delete_requisite_success(client, test_course, test_course2, _db):
    with client:
        # Crear requisito primero
        requisite = Requisite(course_id=test_course.id, course_requisite_id=test_course2.id)
        _db.session.add(requisite)
        _db.session.commit()

        response = client.get(url_for("requisite.delete", requisite_id=requisite.id))

        assert response.status_code == 302
        assert response.location.endswith(
            url_for("course.show", course_id=test_course.id, _external=False)
        )

        # Verificar que se eliminó de la base de datos
        deleted = Requisite.query.get(requisite.id)
        assert deleted is None


def test_delete_nonexistent_requisite(client, _db):
    response = client.get(url_for("requisite.delete", requisite_id=999))
    assert response.status_code == 404


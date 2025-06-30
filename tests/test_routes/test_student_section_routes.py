import json

from flask import get_flashed_messages, url_for

from app.models.student_section import StudentSection


def test_index_open_section(client, test_open_section, test_student, _db):
    student_section = StudentSection(student_id=test_student.id, section_id=test_open_section.id)
    _db.session.add(student_section)
    _db.session.commit()

    url = url_for("student_section.index", section_id=test_open_section.id)
    response = client.get(url)

    assert response.status_code == 200
    assert str(test_student.user.first_name) in response.data.decode()
    assert str(test_student.user.last_name) in response.data.decode()


def test_add_user_to_nonexistent_section(client, _db):
    with client:
        url = url_for("student_section.add_user", section_id=99999)
        response = client.post(url, data={"student_ids": json.dumps([1])}, follow_redirects=True)
        messages = get_flashed_messages()

        assert b"Lista de Secciones" in response.data
        assert "La sección no existe" in messages[0]


def test_add_user_to_closed_section(client, test_closed_section, _db):
    with client:
        url = url_for("student_section.add_user", section_id=test_closed_section.id)
        response = client.get(url, follow_redirects=True)

        messages = get_flashed_messages()
        assert "cerrada y no puede ser modificada" in messages[0]
        assert response.status_code == 200


def test_add_multiple_students(client, test_open_section, test_student, test_student2, _db):
    with client:
        student_ids = [test_student.id, test_student2.id]
        url = url_for("student_section.add_user", section_id=test_open_section.id)

        _response = client.post(
            url, data={"student_ids": json.dumps(student_ids)}, follow_redirects=True
        )

        messages = get_flashed_messages()
        assert "agregados exitosamente" in messages[0]
        assert StudentSection.query.filter_by(section_id=test_open_section.id).count() == 2


def test_add_duplicate_student(client, test_open_section, test_student, _db):
    with client:
        student_section = StudentSection(
            student_id=test_student.id, section_id=test_open_section.id
        )
        _db.session.add(student_section)
        _db.session.commit()

        url = url_for("student_section.add_user", section_id=test_open_section.id)
        _response = client.post(
            url, data={"student_ids": json.dumps([test_student.id])}, follow_redirects=True
        )

        messages = get_flashed_messages()
        assert "ya estaban en esta sección" in messages[0]


def test_remove_student(client, test_open_section, test_student, _db):
    with client:
        student_section = StudentSection(
            student_id=test_student.id, section_id=test_open_section.id
        )
        _db.session.add(student_section)
        _db.session.commit()

        # Remover estudiante
        url = url_for(
            "student_section.remove_user",
            section_id=test_open_section.id,
            student_id=test_student.id,
        )
        response = client.post(url, follow_redirects=True)

        assert response.status_code == 200
        messages = get_flashed_messages()
        assert "removido de la sección" in messages[0]
        assert StudentSection.query.get((test_student.id, test_open_section.id)) is None


def test_add_students_invalid_json(client, test_open_section):
    with client:
        url = url_for("student_section.add_user", section_id=test_open_section.id)

        _response = client.post(url, data={"student_ids": "INVALID_JSON"}, follow_redirects=True)

        messages = get_flashed_messages()
        assert "Error al procesar los estudiantes" in messages[0]


def test_remove_nonexistent_student(client, test_open_section, test_student):
    with client:
        url = url_for(
            "student_section.remove_user",
            section_id=test_open_section.id,
            student_id=test_student.id,
        )
        _response = client.post(url, follow_redirects=True)

        messages = get_flashed_messages()
        assert "Error al remover usuario de la sección." in messages[0]


def test_add_students_mixed_valid_invalid_ids(client, test_open_section, test_student, _db):
    with client:
        valid_id = test_student.id
        invalid_id = 99999
        student_ids = [valid_id, invalid_id]

        url = url_for("student_section.add_user", section_id=test_open_section.id)
        response = client.post(
            url, data={"student_ids": json.dumps(student_ids)}, follow_redirects=True
        )

        messages = get_flashed_messages()
        assert "1 estudiante(s) agregados exitosamente." in messages
        assert b"El estudiante con id 99999 no existe." in response.data


def test_remove_student_get_method_not_allowed(client, test_open_section, test_student, _db):
    with client:
        student_section = StudentSection(
            student_id=test_student.id, section_id=test_open_section.id
        )
        _db.session.add(student_section)
        _db.session.commit()

        url = url_for(
            "student_section.remove_user",
            section_id=test_open_section.id,
            student_id=test_student.id,
        )
        response = client.get(url)

        assert response.status_code == 405


def test_add_students_empty_data(client, test_open_section):
    with client:
        url = url_for("student_section.add_user", section_id=test_open_section.id)
        _response = client.post(url, data={}, follow_redirects=True)

        messages = get_flashed_messages()
        assert "Debes agregar al menos un estudiante." in messages[0]

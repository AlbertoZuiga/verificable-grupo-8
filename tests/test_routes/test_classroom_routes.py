import pytest
from flask import get_flashed_messages, url_for

from app.models.classroom import Classroom


def test_index_empty(client, _db):
    """Test listar salas cuando no hay registros"""
    response = client.get(url_for("classroom.index"))
    assert response.status_code == 200
    assert b"No hay salas registradas." in response.data


def test_index_with_data(client, _db):
    """Test listar salas con registros existentes"""
    classroom1 = Classroom(name="Sala A", capacity=20)
    classroom2 = Classroom(name="Sala B", capacity=30)
    _db.session.add_all([classroom1, classroom2])
    _db.session.commit()

    response = client.get(url_for("classroom.index"))
    assert response.status_code == 200
    assert b"Sala A" in response.data
    assert b"20" in response.data
    assert b"Sala B" in response.data


def test_show_valid_classroom(client, _db):
    """Test mostrar sala existente"""
    classroom = Classroom(name="Sala de Prueba", capacity=25)
    _db.session.add(classroom)
    _db.session.commit()

    response = client.get(url_for("classroom.show", classroom_id=classroom.id))
    assert response.status_code == 200
    assert b"Sala de Prueba" in response.data
    assert b"25" in response.data


def test_show_not_found(client, _db):
    """Test sala no existente"""
    response = client.get(url_for("classroom.show", classroom_id=999))
    assert response.status_code == 404


def test_create_classroom_success(client, _db):
    """Test creación exitosa de sala"""
    with client:
        form_data = {"name": "Nueva Sala", "capacity": "40"}

        response = client.post(url_for("classroom.create"), data=form_data, follow_redirects=True)

        assert response.request.path == url_for("classroom.show", classroom_id=1, _external=False)

        messages = get_flashed_messages()
        assert "Sala creada exitosamente" in messages

        classroom = Classroom.query.first()
        assert classroom.name == "Nueva Sala"
        assert classroom.capacity == 40


def test_create_duplicate_name(client, _db):
    """Test crear sala con nombre duplicado"""
    classroom = Classroom(name="Sala Existente", capacity=10)
    _db.session.add(classroom)
    _db.session.commit()

    form_data = {"name": "Sala Existente", "capacity": "20"}

    response = client.post(url_for("classroom.create"), data=form_data)

    assert b"Ya existe una sala con ese nombre" in response.data

    classrooms = Classroom.query.all()
    assert len(classrooms) == 1


def test_edit_classroom_success(client, _db):
    """Test edición exitosa de sala"""
    with client:
        classroom = Classroom(name="Sala Original", capacity=15)
        _db.session.add(classroom)
        _db.session.commit()

        form_data = {"name": "Sala Modificada", "capacity": "30"}

        response = client.post(
            url_for("classroom.edit", classroom_id=classroom.id),
            data=form_data,
            follow_redirects=True,
        )

        # Verificar redirección
        assert response.request.path == url_for(
            "classroom.show", classroom_id=classroom.id, _external=False
        )

        # Verificar mensaje flash
        messages = get_flashed_messages()
        assert "Sala actualizada exitosamente" in messages

        # Verificar cambios en _db
        updated_classroom = Classroom.query.get(classroom.id)
        assert updated_classroom.name == "Sala Modificada"
        assert updated_classroom.capacity == 30


def test_edit_non_existent(client, _db):
    """Test editar sala inexistente"""
    response = client.post(
        url_for("classroom.edit", classroom_id=999), data={"name": "Invalid", "capacity": 10}
    )
    assert response.status_code == 404


def test_delete_classroom(client, _db):
    """Test eliminación de sala"""
    with client:
        classroom = Classroom(name="Sala a Eliminar", capacity=5)
        _db.session.add(classroom)
        _db.session.commit()
        classroom_id = classroom.id

        response = client.post(
            url_for("classroom.delete", classroom_id=classroom_id), follow_redirects=True
        )

        assert response.request.path == url_for("classroom.index", _external=False)

        messages = get_flashed_messages()
        assert "Sala eliminada exitosamente" in messages

        assert Classroom.query.get(classroom_id) is None


def test_delete_non_existent(client, _db):
    """Test eliminar sala inexistente"""
    response = client.post(url_for("classroom.delete", classroom_id=999))
    assert response.status_code == 404


@pytest.mark.parametrize(
    "form_data, expected_error",
    [
        ({"name": "", "capacity": 20}, b"Este campo es obligatorio."),
        ({"name": "A", "capacity": -5}, b"Debe estar entre 1 y 1000."),
        ({"name": "A", "capacity": 1001}, b"Debe estar entre 1 y 1000."),
        (
            {"name": "A" * 61, "capacity": 10},
            b"Este campo debe tener como maximo 60 caracteres.",
        ),
        ({"name": "Sala Valida"}, b"Este campo es obligatorio."),
    ],
)
def test_invalid_form(client, form_data, expected_error):
    """Test validación de formulario inválido"""
    response = client.post(url_for("classroom.create"), data=form_data)
    assert expected_error in response.data

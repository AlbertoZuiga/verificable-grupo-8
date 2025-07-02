from flask import get_flashed_messages, url_for
from sqlalchemy.exc import SQLAlchemyError

from app.models.evaluation import Evaluation
from app.models.evaluation_instance import EvaluationInstance
from app.models.section import WeighingType


def test_create_evaluation_duplicate_title(client, _db, test_section):
    with client:
        eval1 = Evaluation(
            title="Evaluación Duplicada",
            section=test_section,
            weighing=1,
            weighing_system=WeighingType.PERCENTAGE.name,
        )
        _db.session.add(eval1)
        _db.session.commit()

        data = {
            "title": "Evaluación Duplicada",
            "weighing_system": WeighingType.PERCENTAGE.name,
            "section_id": test_section.id,
        }

        response = client.post(url_for("evaluation.create"), data=data)

        assert (
            b"Ya existe una evaluaci\xc3\xb3n"
            b" con ese t\xc3\xadtulo para la secci\xc3\xb3n."
        ) in response.data
        assert Evaluation.query.count() == 1


def test_create_evaluation_invalid_section(client, _db):
    with client:
        data = {
            "title": "Evaluación Inválida",
            "weighing_system": WeighingType.PERCENTAGE.name,
            "section_id": 9999,
        }

        response = client.post(url_for("evaluation.create"), data=data, follow_redirects=True)
        _messages = get_flashed_messages()

        assert "Debes seleccionar una sección valida".encode("utf-8") in response.data
        assert Evaluation.query.count() == 0


def test_edit_weights_invalid_inputs(client, _db, _test_evaluation):
    with client:
        instance1 = EvaluationInstance(
            title=f"{_test_evaluation.title} 1", evaluation=_test_evaluation, index_in_evaluation=1
        )
        instance2 = EvaluationInstance(
            title=f"{_test_evaluation.title} 2", evaluation=_test_evaluation, index_in_evaluation=2
        )
        _db.session.add_all([instance1, instance2])
        _db.session.commit()

        data = {f"instance_{instance1.id}": "abc", f"instance_{instance2.id}": "xyz"}

        response = client.post(
            url_for("evaluation.edit_instance_weights", evaluation_id=_test_evaluation.id),
            data=data,
            follow_redirects=True,
        )

        assert b"Entrada inv" in response.data
        assert get_flashed_messages()


def test_edit_weights_percentage_invalid_total(client, _db, _test_evaluation):
    with client:
        _test_evaluation.weighing_system = WeighingType.PERCENTAGE
        _db.session.commit()

        instance1 = EvaluationInstance(
            title=f"{_test_evaluation.title} 1", evaluation=_test_evaluation, index_in_evaluation=1
        )
        instance2 = EvaluationInstance(
            title=f"{_test_evaluation.title} 2", evaluation=_test_evaluation, index_in_evaluation=2
        )
        _db.session.add_all([instance1, instance2])
        _db.session.commit()

        data = {f"instance_{instance1.id}": 30.0, f"instance_{instance2.id}": 40.0}

        response = client.post(
            url_for("evaluation.edit_instance_weights", evaluation_id=_test_evaluation.id),
            data=data,
            follow_redirects=True,
        )

        assert (
            b"La suma de los pesos de las instancias debe ser"
            b" 100 para las evaluaciones ponderadas."
        ) in response.data
        assert get_flashed_messages()


def test_edit_weights_points_success(client, _db, _test_evaluation):
    _test_evaluation.weighing_system = WeighingType.WEIGHT
    _db.session.commit()

    instance1 = EvaluationInstance(
        title=f"{_test_evaluation.title} 1", evaluation=_test_evaluation, index_in_evaluation=1
    )
    instance2 = EvaluationInstance(
        title=f"{_test_evaluation.title} 2", evaluation=_test_evaluation, index_in_evaluation=2
    )
    _db.session.add_all([instance1, instance2])
    _db.session.commit()

    data = {f"instance_{instance1.id}": 15.0, f"instance_{instance2.id}": 25.0}

    response = client.post(
        url_for("evaluation.edit_instance_weights", evaluation_id=_test_evaluation.id),
        data=data,
        follow_redirects=True,
    )

    assert b"actualizados correctamente" in response.data
    assert abs(instance1.instance_weighing - 15.0) < 1e-6
    assert abs(instance2.instance_weighing - 25.0) < 1e-6


def test_show_existing_evaluation(client, _db, _test_evaluation):
    response = client.get(url_for("evaluation.show", evaluation_id=_test_evaluation.id))
    assert response.status_code == 200
    assert _test_evaluation.title.encode() in response.data


def test_show_non_existing_evaluation(client, _db):
    response = client.get(url_for("evaluation.show", evaluation_id=999))
    assert response.status_code == 404


def test_delete_non_existent_evaluation(client, _db):
    response = client.get(url_for("evaluation.delete", evaluation_id=999))
    assert response.status_code == 404

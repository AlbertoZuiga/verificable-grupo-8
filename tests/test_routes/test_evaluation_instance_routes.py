# pylint: disable=redefined-outer-name
from flask import get_flashed_messages, url_for
from sqlalchemy.exc import SQLAlchemyError

from app.models.evaluation import Evaluation
from app.models.evaluation_instance import EvaluationInstance
from app.models.section import WeighingType


def test_create_success(client, _db, test_evaluation):
    data = {"title": "Final Exam", "optional": False, "evaluation_id": test_evaluation.id}

    response = client.post(url_for("evaluation_instance.create"), data=data, follow_redirects=True)

    assert response.status_code == 200
    assert b"Final Exam" in response.data
    assert EvaluationInstance.query.count() == 1


def test_create_duplicate_title(client, _db, test_evaluation, test_evaluation_instance):
    with client:
        data = {
            "title": test_evaluation_instance.title,
            "optional": True,
            "evaluation_id": test_evaluation.id,
        }

        _response = client.post(url_for("evaluation_instance.create"), data=data)
        messages = get_flashed_messages()

        assert "ya existe" in messages[0]
        assert EvaluationInstance.query.count() == 1


def test_create_db_error(client, _db, test_evaluation, mocker):
    with client:
        mocker.patch.object(_db.session, "commit", side_effect=SQLAlchemyError("DB error"))

        data = {"title": "Final Exam", "optional": False, "evaluation_id": test_evaluation.id}

        _response = client.post(url_for("evaluation_instance.create"), data=data)
        messages = get_flashed_messages()

        assert "Error creating" in messages[0]
        assert EvaluationInstance.query.count() == 0


def test_edit_success(client, _db, test_evaluation_instance):
    data = {
        "title": "Updated Midterm",
        "optional": True,
        "evaluation_id": test_evaluation_instance.evaluation_id,
    }

    url = url_for("evaluation_instance.edit", evaluation_instance_id=test_evaluation_instance.id)
    response = client.post(url, data=data, follow_redirects=True)

    assert response.status_code == 200
    assert b"Updated Midterm" in response.data

    updated_instance = EvaluationInstance.query.get(test_evaluation_instance.id)
    assert updated_instance.title == "Updated Midterm"


def test_edit_closed_section(client, _db, test_closed_section):
    evaluation_test = Evaluation(
        title="Closed Eval",
        section_id=test_closed_section.id,
        weighing=1,
        weighing_system=WeighingType.WEIGHT,
    )
    _db.session.add(evaluation_test)
    _db.session.commit()

    instance = EvaluationInstance(
        title="Closed Instance",
        evaluation_id=evaluation_test.id,
        index_in_evaluation=1,
        instance_weighing=1,
    )
    _db.session.add(instance)
    _db.session.commit()

    url = url_for("evaluation_instance.edit", evaluation_instance_id=instance.id)
    response = client.get(url)

    assert response.status_code == 302
    assert response.headers["Location"].endswith(
        url_for("section.show", section_id=test_closed_section.id, _external=False)
    )


def test_edit_duplicate_title(client, _db, test_evaluation):
    with client:
        instance1 = EvaluationInstance(
            title="Instance 1",
            evaluation_id=test_evaluation.id,
            index_in_evaluation=1,
            instance_weighing=1,
        )
        instance2 = EvaluationInstance(
            title="Instance 2",
            evaluation_id=test_evaluation.id,
            index_in_evaluation=2,
            instance_weighing=1,
        )
        _db.session.add_all([instance1, instance2])
        _db.session.commit()

        data = {
            "title": instance2.title,
            "optional": True,
            "evaluation_id": test_evaluation.id,
        }

        url = url_for("evaluation_instance.edit", evaluation_instance_id=instance1.id)
        _response = client.post(url, data=data)
        messages = get_flashed_messages()

        assert "ya existe" in messages[0]
        # Verificar que el título no cambió
        db_instance1 = EvaluationInstance.query.get(instance1.id)
        assert db_instance1.title == "Instance 1"


def test_delete_success(client, _db, test_evaluation_instance):
    instance_id = test_evaluation_instance.id
    url = url_for("evaluation_instance.delete", evaluation_instance_id=instance_id)
    response = client.get(url, follow_redirects=True)

    assert response.status_code == 200
    assert EvaluationInstance.query.get(instance_id) is None


def test_delete_closed_section(client, _db, test_closed_section):
    evaluation_test = Evaluation(
        title="Closed Eval",
        section_id=test_closed_section.id,
        weighing=1,
        weighing_system=WeighingType.WEIGHT,
    )
    _db.session.add(evaluation_test)
    _db.session.commit()

    instance = EvaluationInstance(
        title="Closed Instance",
        evaluation_id=evaluation_test.id,
        index_in_evaluation=1,
        instance_weighing=1,
    )
    _db.session.add(instance)
    _db.session.commit()

    instance_id = instance.id
    url = url_for("evaluation_instance.delete", evaluation_instance_id=instance_id)
    response = client.get(url)

    assert response.status_code == 302

    assert response.headers["Location"].endswith(
        url_for("section.show", section_id=test_closed_section.id, _external=False)
    )
    assert EvaluationInstance.query.get(instance_id) is not None


def test_delete_db_error(client, _db, test_evaluation_instance, mocker):
    mocker.patch.object(_db.session, "commit", side_effect=SQLAlchemyError("DB error"))

    instance_id = test_evaluation_instance.id
    url = url_for("evaluation_instance.delete", evaluation_instance_id=instance_id)
    response = client.get(url, follow_redirects=True)

    assert b"Error" not in response.data
    assert EvaluationInstance.query.get(instance_id) is not None


def test_show_success(client, test_evaluation_instance):
    url = url_for("evaluation_instance.show", evaluation_instance_id=test_evaluation_instance.id)
    response = client.get(url)

    assert response.status_code == 200
    assert test_evaluation_instance.title.encode() in response.data


def test_show_not_found(client, _db):
    response = client.get(url_for("evaluation_instance.show", evaluation_instance_id=999))
    assert response.status_code == 404


def test_index_with_instances(client, test_evaluation_instance):
    response = client.get(url_for("evaluation_instance.index"))

    assert response.status_code == 200
    assert test_evaluation_instance.title.encode() in response.data


def test_index_empty(client, _db):
    EvaluationInstance.query.delete()
    _db.session.commit()

    response = client.get(url_for("evaluation_instance.index"))

    assert response.status_code == 200
    assert b"No hay instancias de evaluaciones disponibles." in response.data

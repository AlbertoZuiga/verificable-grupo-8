from flask import url_for

from app.models.user import User


def common_extract_fields(response, fields):
    result = {}
    for field in fields:
        try:
            result[field] = (
                response.data.split(f'name="{field}"'.encode())[1]
                .split(b'value="')[1]
                .split(b'"')[0]
                .decode()
            )
        except IndexError:
            result[field] = None
    return result


def common_test_index_with_multiple(client, endpoint, entity1, entity2):
    response = client.get(url_for(f"{endpoint}.index"))
    assert response.status_code == 200
    assert str(entity1.user.id).encode() in response.data
    assert str(entity2.user.id).encode() in response.data


def common_test_index_empty(client, endpoint, empty_message):
    response = client.get(url_for(f"{endpoint}.index"))
    assert response.status_code == 200
    assert empty_message in response.data


def common_test_show_valid(client, endpoint, entity_id_name, entity_id_value, entity):
    response = client.get(url_for(f"{endpoint}.show", **{entity_id_name: entity_id_value}))
    assert response.status_code == 200
    assert entity.user.first_name.encode() in response.data


def common_test_show_nonexistent(client, endpoint, entity_id_name):
    response = client.get(url_for(f"{endpoint}.show", **{entity_id_name: 99999}))
    assert response.status_code == 404


def common_test_create_duplicate_email(client, endpoint, data, test_user, expected_count):
    data["email"] = test_user.email
    response = client.post(url_for(f"{endpoint}.create"), data=data)
    assert b"Correo ya esta registrado por otro usuario." in response.data
    assert User.query.filter_by(email=test_user.email).count() == expected_count


def common_test_edit_success(client, edit_context):
    endpoint = edit_context["endpoint"]
    entity_id_name = edit_context["entity_id_name"]
    entity_id_value = edit_context["entity_id_value"]
    data = edit_context["data"]
    entity = edit_context["entity"]
    extra_assertions = edit_context.get("extra_assertions")

    url = url_for(f"{endpoint}.edit", **{entity_id_name: entity_id_value})
    response = client.post(url, data=data, follow_redirects=True)
    assert response.status_code == 200
    assert b"actualizado correctamente" in response.data

    assert entity.user.first_name == data["first_name"]
    assert entity.user.last_name == data["last_name"]
    assert entity.user.email == data["email"]

    if extra_assertions:
        extra_assertions(entity, data)


def common_test_edit_duplicate_email(client, edit_context):
    endpoint = edit_context["endpoint"]
    entity_id_name = edit_context["entity_id_name"]
    entity_id_value = edit_context["entity_id_value"]
    data = edit_context["data"]
    entity = edit_context["entity"]
    other_entity = edit_context["other_entity"]

    url = url_for(f"{endpoint}.edit", **{entity_id_name: entity_id_value})
    data["email"] = other_entity.user.email
    response = client.post(url, data=data)
    assert b"Correo ya esta registrado por otro usuario." in response.data

    assert entity.user.email != other_entity.user.email


def common_test_edit_preserve_original_data(client, edit_context):
    endpoint = edit_context["endpoint"]
    entity_id_name = edit_context["entity_id_name"]
    entity_id_value = edit_context["entity_id_value"]
    entity = edit_context["entity"]
    extract_form_data = edit_context["extract_form_data"]

    response = client.get(url_for(f"{endpoint}.edit", **{entity_id_name: entity_id_value}))
    form_data = extract_form_data(response)

    assert form_data["first_name"] == entity.user.first_name
    assert form_data["last_name"] == entity.user.last_name
    assert form_data["email"] == entity.user.email
    if hasattr(entity, "university_entry_year"):
        assert form_data.get("university_entry_year") == str(entity.university_entry_year)


def common_test_delete_success(client, endpoint, entity_id_name, entity_id_value, model):
    response = client.get(
        url_for(f"{endpoint}.delete", **{entity_id_name: entity_id_value}), follow_redirects=True
    )
    assert response.status_code == 200
    assert model.query.get(entity_id_value) is None


def common_test_delete_nonexistent(client, endpoint, entity_id_name):
    response = client.get(
        url_for(f"{endpoint}.delete", **{entity_id_name: 99999}), follow_redirects=True
    )
    assert response.status_code == 404


def common_test_edit_without_email_change(client, edit_context):
    endpoint = edit_context["endpoint"]
    entity_id_name = edit_context["entity_id_name"]
    entity_id_value = edit_context["entity_id_value"]
    entity = edit_context["entity"]
    data = edit_context["data"]

    url = url_for(f"{endpoint}.edit", **{entity_id_name: entity_id_value})
    original_email = entity.user.email
    data["email"] = original_email
    response = client.post(url, data=data, follow_redirects=True)
    assert response.status_code == 200

    assert entity.user.email == original_email

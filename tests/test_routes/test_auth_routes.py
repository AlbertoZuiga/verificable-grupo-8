from urllib.parse import urlparse, parse_qs
import pytest
from flask import url_for

def test_successful_login(client, test_user):
    data = {"email": test_user.email, "password": "testpassword"}
    response = client.post(url_for("auth.login"), data=data, follow_redirects=True)
    assert response.status_code == 200

    assert b"Sesi\xc3\xb3n iniciada" in response.data

def test_login_invalid_email(client, db): # pylint: disable=unused-argument
    data = {"email": "wrong@example.com", "password": "testpassword"}
    response = client.post(url_for("auth.login"), data=data)
    assert response.status_code == 200
    assert b"Usuario o contrase" in response.data

@pytest.mark.parametrize(
    "data,expected_errors",
    [
        ({"email": "", "password": "testpassword"}, ["This field is required."]),
        ({"email": "test@example.com", "password": ""}, ["This field is required."]),
        ({}, ["This field is required.", "This field is required."]),
    ],
)
def test_login_missing_fields(client, data, expected_errors):
    response = client.post(url_for("auth.login"), data=data)
    print("Response:\n",response.data.decode())
    assert response.status_code == 200
    for error in expected_errors:
        assert error.encode() in response.data

def test_logout(client, test_user):
    client.post(
        url_for("auth.login"),
        data={"email": test_user.email, "password": "testpassword"},
    )
    response = client.get(url_for("auth.logout"), follow_redirects=True)
    assert response.status_code == 200

    assert b"Sesi\xc3\xb3n cerrada" in response.data

def test_protected_route_redirect(client):
    response = client.get(url_for("auth.logout"))
    assert response.status_code == 302

    parsed_url = urlparse(response.location)
    assert parsed_url.path == url_for("auth.login", _external=False)

    query_params = parse_qs(parsed_url.query)
    assert "next" in query_params
    assert query_params["next"][0] == url_for("auth.logout", _external=False)

import pytest


def test_index_route(client, mocker):
    mock_schedule = {"key1": {"id": 1, "name": "Clase 1"}, "key2": {"id": 2, "name": "Clase 2"}}
    mocker.patch("app.routes.schedule_routes.get_schedule", return_value=mock_schedule)

    response = client.get("/schedule/")

    assert response.status_code == 200
    assert b"Horario" in response.data


def test_generate_schedule_success(client, mocker):
    mocker.patch("app.routes.schedule_routes.delete_assigned_time_blocks")
    mocker.patch("app.routes.schedule_routes.generate_schedule")

    mock_schedule = {}
    mocker.patch("app.routes.schedule_routes.get_schedule", return_value=mock_schedule)

    response = client.get("/schedule/generate", follow_redirects=True)

    assert response.status_code == 200
    assert b"Horario generado exitosamente" in response.data


def test_generate_schedule_failure(client, mocker):
    mocker.patch("app.routes.schedule_routes.delete_assigned_time_blocks")
    mocker.patch(
        "app.routes.schedule_routes.generate_schedule", side_effect=RuntimeError("Test error")
    )

    mock_schedule = {}
    mocker.patch("app.routes.schedule_routes.get_schedule", return_value=mock_schedule)

    response = client.get("/schedule/generate", follow_redirects=True)

    assert response.status_code == 200
    assert b"Error generando horario: Test error" in response.data


def test_download_schedule_success(client, mocker):
    mock_schedule = {
        "key1": {
            "Curso": "Matemáticas",
            "Sección": "A",
            "Profesor": "Prof A",
            "Día": "Lunes",
            "Hora": "08:00",
        }
    }
    mocker.patch("app.routes.schedule_routes.get_schedule", return_value=mock_schedule)

    response = client.get("/schedule/download")

    assert response.status_code == 200
    assert (
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        in response.headers["Content-Type"]
    )
    assert "attachment; filename=horario.xlsx" in response.headers["Content-Disposition"]

    assert response.data != b"" and len(response.data) > 100


@pytest.mark.parametrize(
    "exception, expected_message",
    [
        (IOError("IO error"), "IO error"),
        (ValueError("Value error"), "Value error"),
        (KeyError("Key error"), "Key error"),
        (TypeError("Type error"), "Type error"),
    ],
)
def test_download_schedule_failures(client, mocker, exception, expected_message):
    mock_get_schedule = mocker.patch("app.routes.schedule_routes.get_schedule")
    mock_get_schedule.side_effect = [exception, {"data": "dummy schedule"}]

    response = client.get("/schedule/download", follow_redirects=True)

    assert response.status_code == 200
    assert b"Error descargando horario" in response.data
    assert expected_message.encode() in response.data


def test_download_unexpected_error(client, mocker):

    mock_get_schedule = mocker.patch("app.routes.schedule_routes.get_schedule")
    mock_get_schedule.side_effect = [TypeError("Unexpected error"), {"data": "dummy schedule"}]

    response = client.get("/schedule/download", follow_redirects=True)

    assert response.status_code == 200
    assert b"Error descargando horario" in response.data
    assert b"Unexpected error" in response.data

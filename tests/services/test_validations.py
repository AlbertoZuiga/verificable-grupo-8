import pytest
from unittest.mock import MagicMock, patch
from app.services import database_validations
from app.services import validations

class DummyModel:
    query = MagicMock()
    some_field = MagicMock()
    f1 = MagicMock()
    f2 = MagicMock()

def test_exists_by_field_found():
    DummyModel.query.filter.return_value.first.return_value = True
    assert database_validations.exists_by_field(DummyModel, "some_field", "value") is True

def test_exists_by_field_not_found():
    DummyModel.query.filter.return_value.first.return_value = None
    assert database_validations.exists_by_field(DummyModel, "some_field", "value") is False

def test_exists_by_two_fields_found():
    DummyModel.query.filter.return_value.first.return_value = True
    assert database_validations.exists_by_two_fields(DummyModel, "f1", "v1", "f2", "v2") is True

def test_exists_by_two_fields_not_found():
    DummyModel.query.filter.return_value.first.return_value = None
    assert database_validations.exists_by_two_fields(DummyModel, "f1", "v1", "f2", "v2") is False

def test_filter_existing_by_field_filters_correctly(monkeypatch):
    monkeypatch.setattr(database_validations, "exists_by_field", lambda m, f, v: v == "exists")
    class Obj: pass
    obj1 = Obj(); setattr(obj1, "some_field", "exists")
    obj2 = Obj(); setattr(obj2, "some_field", "not_exists")
    result = database_validations.filter_existing_by_field(DummyModel, "some_field", [obj1, obj2])
    assert result == [obj2]

def test_filter_existing_by_two_fields_filters_correctly(monkeypatch):
    monkeypatch.setattr(database_validations, "exists_by_two_fields", lambda m, f1, v1, f2, v2: v1 == "exists")
    class Obj: pass
    obj1 = Obj(); setattr(obj1, "f1", "exists"); setattr(obj1, "f2", "x")
    obj2 = Obj(); setattr(obj2, "f1", "not_exists"); setattr(obj2, "f2", "y")
    result = database_validations.filter_existing_by_two_fields(DummyModel, "f1", "f2", [obj1, obj2])
    assert result == [obj2]

@patch("app.services.database_validations.EvaluationInstance")
@patch("app.services.database_validations.StudentEvaluationInstance")
@patch("app.services.database_validations.exists_by_two_fields")
def test_filter_grades_filters_correctly(mock_exists, mock_StudentEval, mock_EvalInstance):
    parsed_data = [
        {"topic_id": 1, "instance_index": 1, "student_id": 10, "grade": 7.0},
        {"topic_id": 2, "instance_index": 2, "student_id": 20, "grade": 6.0},
        {"topic_id": 3, "instance_index": 3, "student_id": 30, "grade": 5.0},
    ]
    # First exists, second missing eval_instance, third grade exists
    mock_EvalInstance.query.filter_by.side_effect = [
        MagicMock(first=MagicMock(return_value=MagicMock(id=101))),
        MagicMock(first=MagicMock(return_value=None)),
        MagicMock(first=MagicMock(return_value=MagicMock(id=303))),
    ]
    mock_exists.side_effect = [False, True, True]  # Only first is appended
    mock_StudentEval.side_effect = lambda **kwargs: kwargs

    result = database_validations.filter_grades(parsed_data)

    assert len(result) == 1
    assert result[0]["evaluation_instance_id"] == 101
    assert result[0]["student_id"] == 10
    assert result[0]["grade"] == 7.0

@patch("app.services.validations.Section")
@patch("app.services.validations.flash")
def test_validate_section_for_evaluation_invalid_section(mock_flash, mock_section):
    # Mock section does not exist
    mock_section.query.get.return_value = None

    # Call the function
    result = validations.validate_section_for_evaluation(1)

    # Assert the result
    assert result is True
    mock_flash.assert_called_once_with("ID de sección invalido", "danger")


@patch("app.services.validations.Section")
@patch("app.services.validations.flash")
def test_validate_section_for_evaluation_closed_section(mock_flash, mock_section):
    # Mock section exists and is closed
    mock_section.query.get.return_value = MagicMock(closed=True)

    # Call the function
    result = validations.validate_section_for_evaluation(1)

    # Assert the result
    assert result is True
    mock_flash.assert_called_once_with("Sección cerrada.", "warning")


@patch("app.services.validations.Section")
@patch("app.services.validations.flash")
def test_validate_section_for_evaluation_valid_section(mock_flash, mock_section):
    # Mock section exists and is not closed
    mock_section.query.get.return_value = MagicMock(closed=False)

    # Call the function
    result = validations.validate_section_for_evaluation(1)

    # Assert the result
    assert result is None
    mock_flash.assert_not_called()
import pytest
from unittest.mock import patch, MagicMock
from app.services import section_service


@patch("app.services.section_service.kanvas_db")
@patch("app.services.section_service.Section")
def test_create_section_success(mock_section, mock_db):
    # Mock the Section model and database session
    mock_section.return_value = MagicMock()
    mock_db.session.add = MagicMock()
    mock_db.session.commit = MagicMock()

    # Call the function
    section = section_service.create_section(1, 2, "SEC001", "PERCENTAGE")

    # Assert the section was created successfully
    mock_db.session.add.assert_called_once_with(mock_section.return_value)
    mock_db.session.commit.assert_called_once()
    assert section == mock_section.return_value


@patch("app.services.section_service.kanvas_db")
@patch("app.services.section_service.Section")
def test_create_section_missing_fields(mock_section, mock_db):
    # Call the function with missing fields and assert it raises ValueError
    with pytest.raises(ValueError, match="Todos los campos son obligatorios."):
        section_service.create_section(None, 2, "SEC001", "PERCENTAGE")


@patch("app.services.section_service.kanvas_db")
@patch("app.services.section_service.Section")
def test_create_section_database_error(mock_section, mock_db):
    # Mock the database session to raise an exception
    mock_db.session.add = MagicMock()
    mock_db.session.commit.side_effect = Exception("Database error")
    mock_db.session.rollback = MagicMock()

    # Call the function and assert it raises the exception
    with pytest.raises(Exception, match="Database error"):
        section_service.create_section(1, 2, "SEC001", "PERCENTAGE")

    # Assert rollback was called
    mock_db.session.rollback.assert_called_once()
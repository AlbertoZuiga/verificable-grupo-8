import pytest
from unittest.mock import patch, MagicMock
from app.services import student_section_service


@patch("app.services.student_section_service.Section")
@patch("app.services.student_section_service.Student")
def test_get_students_not_in_section(mock_student, mock_section):
    # Mock section with students
    mock_section.query.get_or_404.return_value.students = [MagicMock(id=1), MagicMock(id=2)]
    # Mock students not in section
    mock_student.query.filter.return_value.all.return_value = ["student3", "student4"]

    # Call the function
    result = student_section_service.get_students_not_in_section(1)

    # Assert the result
    assert result == ["student3", "student4"]
    mock_section.query.get_or_404.assert_called_once_with(1)
    mock_student.query.filter.assert_called_once()


@patch("app.services.student_section_service.StudentSection")
@patch("app.services.student_section_service.kanvas_db")
def test_remove_student_from_section_success(mock_db, mock_student_section):
    # Mock student_section exists
    mock_student_section.query.filter_by.return_value.first.return_value = MagicMock()

    # Call the function
    result = student_section_service.remove_student_from_section(1, 2)

    # Assert success
    assert result is True
    mock_db.session.delete.assert_called_once()
    mock_db.session.commit.assert_called_once()


import pytest
from unittest.mock import MagicMock, patch
from app.services import course_service

@patch("app.services.course_service.Course")
def test_get_course_and_other_courses(mock_course):
    # Setup
    mock_instance = MagicMock()
    mock_instance.prerequisites = [MagicMock(course_requisite_id=2), MagicMock(course_requisite_id=3)]
    mock_course.query.get_or_404.return_value = mock_instance
    mock_course.query.filter.return_value.all.return_value = ["other_course1", "other_course2"]

    # Execute
    course, courses = course_service.get_course_and_other_courses(1)

    # Assert
    assert course == mock_instance
    assert courses == ["other_course1", "other_course2"]
    mock_course.query.get_or_404.assert_called_once_with(1)
    mock_course.query.filter.assert_called()
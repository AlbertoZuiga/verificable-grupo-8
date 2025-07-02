import pytest
from unittest.mock import MagicMock, patch
from app.services import generate_schedule


@patch("app.services.generate_schedule.kanvas_db")
@patch("app.services.generate_schedule.AssignedTimeBlock")
def test_delete_assigned_time_blocks(mock_assigned_time_block, mock_db):
    mock_db.session.query.return_value.delete.return_value = None
    generate_schedule.delete_assigned_time_blocks()
    mock_db.session.query.assert_called_once_with(mock_assigned_time_block)
    mock_db.session.commit.assert_called_once()


@patch("app.services.generate_schedule.TimeBlock")
@patch("app.services.generate_schedule.kanvas_db")
def test_create_block_range(mock_db, mock_time_block):
    mock_time_block.query.filter_by.return_value.first.return_value = None
    generate_schedule._create_block_range(9, 11, 60)
    assert mock_db.session.add.call_count > 0


@patch("app.services.generate_schedule._create_block_range")
@patch("app.services.generate_schedule.kanvas_db")
def test_create_time_blocks(mock_db, mock_create_block_range):
    generate_schedule._create_time_blocks()
    mock_create_block_range.assert_any_call(9, 13, 60)
    mock_create_block_range.assert_any_call(14, 18, 60)
    mock_db.session.commit.assert_called_once()

@patch("app.services.generate_schedule.TimeBlock")
def test_group_blocks_by_day(mock_time_block):
    mock_time_block.weekday = "Lunes"
    mock_time_block.start_time = "09:00"
    blocks = [mock_time_block]
    result = generate_schedule._group_blocks_by_day(blocks)
    assert "Lunes" in result
    assert len(result["Lunes"]) == 1


@patch("app.services.generate_schedule.TimeBlock")
def test_get_contiguous_sequences(mock_time_block):
    mock_time_block.start_time = "09:00"
    mock_time_block.stop_time = "10:00"
    blocks = [mock_time_block]
    result = generate_schedule._get_contiguous_sequences(blocks)
    assert len(result) == 1
    assert len(result[0]) == 1


@patch("app.services.generate_schedule.Section")
@patch("app.services.generate_schedule.Classroom")
@patch("app.services.generate_schedule.TimeBlock")
@patch("app.services.generate_schedule.kanvas_db")
def test_assign_section_if_possible(mock_db, mock_time_block, mock_classroom, mock_section):
    mock_section.course_instance.course.credits = 3
    mock_time_block.weekday = "Lunes"
    mock_time_block.start_time = "09:00"
    mock_time_block.stop_time = "10:00"
    blocks = [mock_time_block]
    classrooms = [mock_classroom]
    result = generate_schedule._assign_section_if_possible(mock_section, classrooms, blocks)
    assert result is False


@patch("app.services.generate_schedule.AssignedTimeBlock")
@patch("app.services.generate_schedule.kanvas_db")
def test_assign_blocks(mock_db, mock_assigned_time_block):
    mock_time_block = MagicMock(id=1)
    generate_schedule._assign_blocks(1, 1, [mock_time_block])
    mock_db.session.add.assert_called_once()
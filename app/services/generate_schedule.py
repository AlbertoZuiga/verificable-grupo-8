from collections import defaultdict
from datetime import datetime, timedelta

from app.extensions import kanvas_db
from app.models.assigned_time_block import AssignedTimeBlock
from app.models.classroom import Classroom
from app.models.course import Course
from app.models.course_instance import CourseInstance
from app.models.section import Section
from app.models.student import Student
from app.models.student_section import StudentSection
from app.models.time_block import TimeBlock

DAYS = {
    1: "Lunes",
    2: "Martes",
    3: "Miércoles",
    4: "Jueves",
    5: "Viernes",
}

MORNING_START = 9
MORNING_END = 13

AFTERNOON_START = 14
AFTERNOON_END = 18

BLOCK_DURATION = 60


class ScheduleAssignmentError(Exception):
    pass


def delete_assigned_time_blocks():
    """
    Delete all assigned time blocks from the database.
    """
    kanvas_db.session.query(AssignedTimeBlock).delete()
    kanvas_db.session.commit()


def _create_block_range(start_hour, end_hour, duration):
    """
    Create time blocks between given start and end hours, for each weekday.
    """
    for hour in range(start_hour, end_hour):
        for day_num, day_name in DAYS.items():
            block_id = (hour - 1) * len(DAYS) + day_num
            time_block = TimeBlock.query.filter_by(id=block_id).first()

            start = datetime.strptime(f"{hour:02d}:00", "%H:%M")
            stop = start + timedelta(minutes=duration)

            if not time_block:
                time_block = TimeBlock(
                    id=block_id,
                    start_time=start.strftime("%H:%M"),
                    stop_time=stop.strftime("%H:%M"),
                    weekday=day_name,
                )
            else:
                time_block.start_time = start.strftime("%H:%M")
                time_block.stop_time = stop.strftime("%H:%M")
                time_block.weekday = day_name

            kanvas_db.session.add(time_block)


def _create_time_blocks():
    """
    Create all time blocks for morning and afternoon sessions.
    """
    _create_block_range(MORNING_START, MORNING_END, BLOCK_DURATION)
    _create_block_range(AFTERNOON_START, AFTERNOON_END, BLOCK_DURATION)
    kanvas_db.session.commit()


def generate_schedule():
    """
    Generate the schedule by assigning sections to classrooms and time blocks.
    """
    _create_time_blocks()

    sections = (
        kanvas_db.session.query(Section)
        .join(CourseInstance)
        .join(Course)
        .outerjoin(StudentSection)
        .group_by(Section.id)
        .order_by(
            kanvas_db.func.count(StudentSection.student_id).desc(),
            Course.credits.desc(),
        )
        .all()
    )

    classrooms = kanvas_db.session.query(Classroom).all()
    time_blocks = kanvas_db.session.query(TimeBlock).order_by(TimeBlock.id).all()

    for section in sections:
        if _assign_section_if_possible(section, classrooms, time_blocks):
            continue
        raise ScheduleAssignmentError(f"No se pudo asignar la sección {section.id}")

    kanvas_db.session.commit()


def _group_blocks_by_day(time_blocks):
    blocks_by_day = defaultdict(list)
    for tb in time_blocks:
        blocks_by_day[tb.weekday].append(tb)
    for blocks in blocks_by_day.values():
        blocks.sort(key=lambda b: b.start_time)
    return blocks_by_day


def _get_contiguous_sequences(blocks):
    sequences = []
    if not blocks:
        return sequences
    current_sequence = [blocks[0]]
    for block in blocks[1:]:
        prev_end = current_sequence[-1].stop_time
        current_start = block.start_time
        if current_start == prev_end:
            current_sequence.append(block)
        else:
            sequences.append(current_sequence)
            current_sequence = [block]
    if current_sequence:
        sequences.append(current_sequence)
    return sequences


def _assign_section_if_possible(section, classrooms, time_blocks):
    required_blocks = section.course_instance.course.credits
    blocks_by_day = _group_blocks_by_day(time_blocks)

    for day, blocks in blocks_by_day.items():
        sequences = _get_contiguous_sequences(blocks)
        if _try_assign_from_sequences(section, classrooms, sequences, required_blocks, day):
            return True

    return False


def _try_assign_from_sequences(section, classrooms, sequences, required_blocks, day):
    for sequence in sequences:
        if len(sequence) < required_blocks:
            continue

        if _try_assign_from_sequence(section, classrooms, sequence, required_blocks, day):
            return True

    return False


def _try_assign_from_sequence(section, classrooms, sequence, required_blocks, day):
    for i in range(len(sequence) - required_blocks + 1):
        candidate_time_blocks = sequence[i : i + required_blocks]

        for classroom in classrooms:
            if _is_valid_assignment(section, classroom.id, candidate_time_blocks):
                _assign_blocks(section.id, classroom.id, candidate_time_blocks)
                print(
                    f"Sección {section.id} asignada en sala {classroom.name}, "
                    f"{day}, bloques {[tb.id for tb in candidate_time_blocks]}"
                )
                return True
    return False


def _is_valid_assignment(section, classroom_id, time_blocks):
    """
    Check if the assignment of a section to a classroom and time blocks is valid.
    """
    classroom = _get_classroom(classroom_id)
    num_students = _get_student_count(section.id)

    has_enough_capacity = _has_capacity(classroom, num_students)
    blocks_available = not _are_blocks_taken(classroom_id, time_blocks)
    teacher_free = not _has_schedule_conflict(section.teacher_id, time_blocks)
    students_free = not _students_have_conflict(section.id, time_blocks)

    return has_enough_capacity and blocks_available and teacher_free and students_free


def _get_classroom(classroom_id):
    """
    Retrieve a classroom by its ID.
    """
    return kanvas_db.session.query(Classroom).filter_by(id=classroom_id).first()


def _get_student_count(section_id):
    """
    Return the number of students enrolled in a given section.
    """
    return kanvas_db.session.query(StudentSection).filter_by(section_id=section_id).count()


def _has_capacity(classroom, num_students):
    """
    Check if the classroom has enough capacity for the number of students.
    """
    return classroom.capacity >= num_students


def _assign_blocks(section_id, classroom_id, time_blocks):
    """
    Assign given time blocks to a section in a specific classroom.
    """
    for time_block in time_blocks:
        assignment = AssignedTimeBlock(
            section_id=section_id,
            classroom_id=classroom_id,
            time_block_id=time_block.id,
        )
        kanvas_db.session.add(assignment)


def _are_blocks_taken(classroom_id, time_blocks):
    """
    Check if any of the given time blocks are already taken in the classroom.
    """
    time_block_ids = [tb.id for tb in time_blocks]
    assigned = (
        kanvas_db.session.query(AssignedTimeBlock)
        .filter(
            AssignedTimeBlock.classroom_id == classroom_id,
            AssignedTimeBlock.time_block_id.in_(time_block_ids),
        )
        .first()
    )
    return assigned is not None


def _has_schedule_conflict(teacher_id, time_blocks):
    """
    Check if the teacher has a scheduling conflict with the given time blocks.
    """
    time_block_ids = [tb.id for tb in time_blocks]
    return _teacher_has_assigned_blocks(teacher_id, time_block_ids)


def _teacher_has_assigned_blocks(teacher_id, time_block_ids):
    """
    Check if a teacher has been assigned any of the specified time blocks.
    """
    assigned = (
        kanvas_db.session.query(AssignedTimeBlock)
        .join(Section)
        .filter(
            Section.teacher_id == teacher_id,
            AssignedTimeBlock.time_block_id.in_(time_block_ids),
        )
        .first()
    )
    return assigned is not None


def _students_have_conflict(section_id, time_blocks):
    """
    Check if any student in the section has a scheduling conflict with the given time blocks.
    """
    student_ids = _get_student_ids_from_section(section_id)
    time_block_ids = [tb.id for tb in time_blocks]

    return _has_conflict_with_time_blocks(student_ids, time_block_ids)


def _get_student_ids_from_section(section_id):
    """
    Retrieve a list of student IDs enrolled in a specific section.
    """
    student_id_tuples = (
        kanvas_db.session.query(Student.id)
        .join(StudentSection)
        .filter(StudentSection.section_id == section_id)
        .all()
    )
    return [sid for (sid,) in student_id_tuples]


def _has_conflict_with_time_blocks(student_ids, time_block_ids):
    """
    Check if any of the students have already been assigned the given time blocks.
    """
    assigned = (
        kanvas_db.session.query(AssignedTimeBlock)
        .join(Section)
        .join(StudentSection)
        .filter(
            StudentSection.student_id.in_(student_ids),
            AssignedTimeBlock.time_block_id.in_(time_block_ids),
        )
        .first()
    )
    return assigned is not None


def get_schedule():
    raw_schedule = _fetch_assigned_time_blocks()
    return _build_clean_schedule(raw_schedule)


def _fetch_assigned_time_blocks():
    return (
        kanvas_db.session.query(AssignedTimeBlock)
        .join(TimeBlock, TimeBlock.id == AssignedTimeBlock.time_block_id)
        .order_by(TimeBlock.start_time)
        .all()
    )


def _build_clean_schedule(schedule):
    clean_schedule = {}
    for entry in schedule:
        section_id = entry.section_id
        if section_id not in clean_schedule:
            clean_schedule[section_id] = _build_schedule_entry(entry)
        else:
            clean_schedule[section_id]["stop_time"] = entry.time_block.stop_time.strftime("%H:%M")
    return clean_schedule


def _build_schedule_entry(entry):
    return {
        "course_title": entry.section.course_instance.course.title,
        "course_code": entry.section.course_instance.course.code,
        "section_code": entry.section.code,
        "classroom": entry.classroom.name,
        "weekday": entry.time_block.weekday,
        "start_time": entry.time_block.start_time.strftime("%H:%M"),
        "stop_time": entry.time_block.stop_time.strftime("%H:%M"),
    }

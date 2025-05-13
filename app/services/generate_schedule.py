from app import app, kanvas_db
from app.models import (
    Course, CourseInstance, Semester, Section, WeighingType, Requisite, User, 
    Teacher, Evaluation, EvaluationInstance, StudentSection, Classroom, 
    TimeBlock, AssignedTimeBlock, Student
)


DAYS = {
    1: "Lunes",
    2: "Martes",
    3: "Miércoles",
    4: "Jueves",
    5: "Viernes"
}


MORNING_START = 9
MORNING_END = 13

AFTERNOON_START = 14
AFTERNOON_END = 18

BLOCK_DURATION_MORNING = 50
BLOCK_DURATION_AFTERNOON = 60


def delete_assigned_time_blocks():
    """
    Delete all assigned time blocks from the database.
    """
    kanvas_db.session.query(AssignedTimeBlock).delete()
    kanvas_db.session.commit()


def create_block_range(start_hour, end_hour, duration):
    """
    Create time blocks between given start and end hours, for each weekday.
    """
    for hour in range(start_hour, end_hour):
        for day_num, day_name in DAYS.items():
            block_id = (hour - 1) * len(DAYS) + day_num
            time_block = TimeBlock.query.filter_by(id=block_id).first()
            if not time_block:
                time_block = TimeBlock(
                    id=block_id,
                    start_time=f"{hour:02d}:00",
                    stop_time=f"{hour+1:02d}:{duration:02d}",
                    weekday=day_name
                )
                kanvas_db.session.add(time_block)


def create_time_blocks():
    """
    Create all time blocks for morning and afternoon sessions.
    """
    create_block_range(MORNING_START, MORNING_END, BLOCK_DURATION_MORNING)
    create_block_range(AFTERNOON_START, AFTERNOON_END, BLOCK_DURATION_AFTERNOON)
    kanvas_db.session.commit()


def generate_schedule():
    """
    Generate the schedule by assigning sections to classrooms and time blocks.
    """
    create_time_blocks()

    sections = (
        kanvas_db.session.query(Section)
        .join(CourseInstance)
        .join(Course)
        .outerjoin(StudentSection)
        .group_by(Section.id)
        .order_by(
            kanvas_db.func.count(StudentSection.student_id).desc(),
            Course.credits.desc()
        ).all()
    )

    classrooms = kanvas_db.session.query(Classroom).all()
    time_blocks = kanvas_db.session.query(TimeBlock).order_by(TimeBlock.id).all()

    for section in sections:
        if assign_section_if_possible(section, classrooms, time_blocks):
            continue
        raise Exception(f"No se pudo asignar la sección {section.id}")

    kanvas_db.session.commit()


def assign_section_if_possible(section, classrooms, time_blocks):
    """
    Try to assign a section to available classrooms and time blocks.
    Return True if assignment is successful, False otherwise.
    """
    required_blocks = section.course_instance.course.credits
    for i in range(len(time_blocks) - required_blocks + 1):
        candidate_time_blocks = time_blocks[i:i + required_blocks]
        for classroom in classrooms:
            if is_valid_assignment(section, classroom.id, candidate_time_blocks):
                assign_blocks(section.id, classroom.id, candidate_time_blocks)
                app.logger.info(f"Sección {section.id} asignada en sala {classroom.name}, bloques {[tb.id for tb in candidate_time_blocks]}")
                return True
    return False


def is_valid_assignment(section, classroom_id, time_blocks):
    """
    Check if the assignment of a section to a classroom and time blocks is valid.
    """
    classroom = get_classroom(classroom_id)
    num_students = get_student_count(section.id)
    return (
        has_capacity(classroom, num_students) and
        not are_blocks_taken(classroom_id, time_blocks) and
        not has_schedule_conflict(section.teacher_id, time_blocks) and
        not students_have_conflict(section.id, time_blocks)
    )


def get_classroom(classroom_id):
    """
    Retrieve a classroom by its ID.
    """
    return kanvas_db.session.query(Classroom).filter_by(id=classroom_id).first()


def get_student_count(section_id):
    """
    Return the number of students enrolled in a given section.
    """
    return kanvas_db.session.query(StudentSection).filter_by(section_id=section_id).count()


def has_capacity(classroom, num_students):
    """
    Check if the classroom has enough capacity for the number of students.
    """
    return classroom.capacity >= num_students


def assign_blocks(section_id, classroom_id, time_blocks):
    """
    Assign given time blocks to a section in a specific classroom.
    """
    for time_block in time_blocks:
        assignment = AssignedTimeBlock(
            section_id=section_id,
            classroom_id=classroom_id,
            time_block_id=time_block.id
        )
        kanvas_db.session.add(assignment)


def are_blocks_taken(classroom_id, time_blocks):
    """
    Check if any of the given time blocks are already taken in the classroom.
    """
    time_block_ids = [tb.id for tb in time_blocks]
    return kanvas_db.session.query(AssignedTimeBlock).filter(
        AssignedTimeBlock.classroom_id == classroom_id,
        AssignedTimeBlock.time_block_id.in_(time_block_ids)
    ).first() is not None


def has_schedule_conflict(teacher_id, time_blocks):
    """
    Check if the teacher has a scheduling conflict with the given time blocks.
    """
    time_block_ids = [tb.id for tb in time_blocks]
    return teacher_has_assigned_blocks(teacher_id, time_block_ids)


def teacher_has_assigned_blocks(teacher_id, time_block_ids):
    """
    Check if a teacher has been assigned any of the specified time blocks.
    """
    return kanvas_db.session.query(AssignedTimeBlock).join(Section).filter(
        Section.teacher_id == teacher_id,
        AssignedTimeBlock.time_block_id.in_(time_block_ids)
    ).first() is not None


def students_have_conflict(section_id, time_blocks):
    """
    Check if any student in the section has a scheduling conflict with the given time blocks.
    """
    student_ids = get_student_ids_from_section(section_id)

    time_block_ids = [tb.id for tb in time_blocks]
    return has_conflict_with_time_blocks(student_ids, time_block_ids)


def get_student_ids_from_section(section_id):
    """
    Retrieve a list of student IDs enrolled in a specific section.
    """
    return [sid for (sid,) in kanvas_db.session.query(Student.id)
            .join(StudentSection)
            .filter(StudentSection.section_id == section_id)
            .all()]


def extract_time_block_ids(time_blocks):
    """
    Extract the IDs from a list of time block objects.
    """
    return [tb.id for tb in time_blocks]


def has_conflict_with_time_blocks(student_ids, time_block_ids):
    """
    Check if any of the students have already been assigned the given time blocks.
    """
    return kanvas_db.session.query(AssignedTimeBlock).join(Section).join(StudentSection).filter(
        StudentSection.student_id.in_(student_ids),
        AssignedTimeBlock.time_block_id.in_(time_block_ids)
    ).first() is not None


if __name__ == "__main__":
    with app.app_context():
        app.logger.info("Generando el horario...")
        delete_assigned_time_blocks()
        generate_schedule()
        app.logger.info("Horario generado con éxito.")
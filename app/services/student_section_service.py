from flask import flash
from sqlalchemy.exc import SQLAlchemyError

from app.extensions import kanvas_db
from app.models.section import Section
from app.models.student import Student
from app.models.student_section import StudentSection


def get_students_not_in_section(section_id):
    section = Section.query.get_or_404(section_id)
    section_student_ids = [student.id for student in section.students]
    return Student.query.filter(Student.id.notin_(section_student_ids)).all()


def add_student_to_section(student_id, section_id):
    student = Student.query.get(student_id)
    if student is None:
        flash(f"El estudiante con id {student_id} no existe.", "danger")
        return False
    existing_student_section = StudentSection.query.filter_by(
        student_id=student_id, section_id=section_id
    ).first()
    if existing_student_section:
        print("El estudiante ya está en esta sección.")
        return False

    new_student_section = StudentSection(student_id=student_id, section_id=section_id)
    try:
        kanvas_db.session.add(new_student_section)
        kanvas_db.session.commit()
        return True
    except SQLAlchemyError as e:
        kanvas_db.session.rollback()
        print(f"Error al agregar usuario a la sección: {str(e)}")
        return False


def remove_student_from_section(section_id, student_id):
    student_section = StudentSection.query.filter_by(
        section_id=section_id, student_id=student_id
    ).first()
    try:
        kanvas_db.session.delete(student_section)
        kanvas_db.session.commit()
        return True
    except SQLAlchemyError as e:
        kanvas_db.session.rollback()
        print(f"Error al remover usuario de la sección: {e}")
        return False

from app import kanvas_db
from app.models import Section, Student, StudentSection


def get_students_not_in_section(section_id):
    section = Section.query.get_or_404(section_id)
    section_student_ids = [student.id for student in section.students]
    return Student.query.filter(Student.id.notin_(section_student_ids)).all()


def add_student_to_section(student_id, section_id):
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
    except Exception as e:
        kanvas_db.session.rollback()
        print(f"Error al agregar usuario a la sección: {str(e)}")
        return False


def remove_student_from_section(section_id, student_id):
    student_section = StudentSection.query.filter_by(
        section_id=section_id, student_id=student_id
    ).first_or_404()
    try:
        kanvas_db.session.delete(student_section)
        kanvas_db.session.commit()
        return True
    except Exception as e:
        kanvas_db.session.rollback()
        print(f"Error al remover usuario de la sección: {e}")
        return False


def _add_student_to_section(section_id, student_id):
    print(f"Intentando agregar estudiante {student_id} a sección {section_id}")
    section = Section.query.get(section_id)
    if not section:
        raise ValueError(f"Section with id {section_id} not found.")

    existing_ids = {s.id for s in section.students}
    if student_id in existing_ids:
        print(
            f"⏭️  Estudiante {student_id} ya está en la sección {section_id}, se omite."
        )
        return 0

    new_link = StudentSection(student_id=student_id, section_id=section_id)
    try:
        kanvas_db.session.add(new_link)
        kanvas_db.session.commit()
        print(
            f"✅ Estudiante {student_id} agregado correctamente a la sección {section_id}"
        )
        return 1
    except Exception as e:
        kanvas_db.session.rollback()
        raise RuntimeError(f"Error al agregar estudiante a la sección: {str(e)}")

from app import kanvas_db
from app.models import StudentSection, Student, Section

def get_students_not_in_section(section_id):
    section = Section.query.get_or_404(section_id)
    section_student_ids = [student.id for student in section.students]
    return Student.query.filter(Student.id.notin_(section_student_ids)).all()

def add_student_to_section(student_id, section_id):
    existing_student_section = StudentSection.query.filter_by(student_id=student_id, section_id=section_id).first()
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
    student_section = StudentSection.query.filter_by(section_id=section_id, student_id=student_id).first_or_404()
    try:
        kanvas_db.session.delete(student_section)
        kanvas_db.session.commit()
        return True
    except Exception as e:
        kanvas_db.session.rollback()
        print(f"Error al remover usuario de la sección: {e}")
        return False

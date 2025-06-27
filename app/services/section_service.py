from app import kanvas_db
from app.models.section import Section


def create_section(course_instance_id, teacher_id, code, weighing_type):
    if not course_instance_id or not teacher_id or not code or not weighing_type:
        raise ValueError("Todos los campos son obligatorios.")

    new_section = Section(
        course_instance_id=course_instance_id,
        teacher_id=teacher_id,
        code=code,
        weighing_type=weighing_type,
    )
    try:
        kanvas_db.session.add(new_section)
        kanvas_db.session.commit()
        return new_section
    except Exception as e:
        kanvas_db.session.rollback()
        raise e

from app.extensions import kanvas_db
from app.models.course import Course
from app.models.requisite import Requisite


# Necessary becuase the json only provides course code. Need ids to create the requisite
def build_requisite_objects_from_codes(code_pairs):
    valid = []
    skipped = []

    for main_code, req_code in code_pairs:
        main = Course.query.filter_by(code=main_code).first()
        req = Course.query.filter_by(code=req_code).first()

        if not main or not req:
            skipped.append((main_code, req_code, "missing_course"))
            continue

        valid.append(Requisite(course_id=main.id, course_requisite_id=req.id))

    return valid, skipped


def add_objects_to_session(instances) -> int:
    objects_created_count = 0
    for instance in instances:
        kanvas_db.session.add(instance)
        objects_created_count += 1
    return objects_created_count

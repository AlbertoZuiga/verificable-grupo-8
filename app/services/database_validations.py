from app.models import EvaluationInstance, StudentEvaluationInstance

def exists_by_field(model, field_name: str, value) -> bool:
    return model.query.filter(getattr(model, field_name) == value).first() is not None

def exists_by_two_fields(model, field_1: str, value_1, field_2: str, value_2) -> bool:
    return model.query.filter(
        getattr(model, field_1) == value_1,
        getattr(model, field_2) == value_2
    ).first() is not None

def filter_existing_by_field(model, field_name: str, objects) -> list:
    return [obj for obj in objects if not exists_by_field(model, field_name, getattr(obj, field_name))]

def filter_existing_by_two_fields(model, field_1: str, field_2: str, objects) -> list:
    return [
        obj for obj in objects
        if not exists_by_two_fields(
            model,
            field_1, getattr(obj, field_1),
            field_2, getattr(obj, field_2)
        )
    ]

def filter_grades(parsed_data: list) -> list:
    filtered_grades = []

    for entry in parsed_data:
        topic_id = entry["topic_id"]
        instance_index = entry["instance_index"]
        student_id = entry["student_id"]

        eval_instance = EvaluationInstance.query.filter_by(
            evaluation_id=topic_id,
            index_in_evaluation=instance_index
        ).first()

        if not eval_instance:
            entry["__reason__"] = "missing_eval_instance"
            continue

        if exists_by_two_fields(
            StudentEvaluationInstance,
            "evaluation_instance_id", eval_instance.id,
            "student_id", student_id
        ):
            entry["__reason__"] = "grade_exists"
            continue

        filtered_grades.append({
            "evaluation_instance_id": eval_instance.id,
            "student_id": student_id,
            "grade": entry["grade"]
        })

    return filtered_grades
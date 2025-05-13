from flask import flash

from app.models import (
    Evaluation,
    EvaluationInstance,
    Student,
    StudentEvaluationInstance,
    StudentSection,
    Teacher,
    User,
    Course,
    CourseInstance,
    Section,
    Classroom,
    Requisite,
    WeighingType,
    Semester,
)

def flash_successful_load(count, entity):
    message = f"{count} {entity} loaded successfully."
    flash(message, "success")

# Created to handle grades, which is a special case
def flash_invalid_grades(parsed_data: list):
    for entry in parsed_data:
        reason = entry.get("__reason__")
        topic_id = entry.get("topic_id")
        index = entry.get("instance_index")
        student_id = entry.get("student_id")

        if reason == "missing_eval_instance":
            flash(f"No EvaluationInstance found for topic ID {topic_id} and index {index}. Skipping.", "warning")

        elif reason == "grade_exists":
            flash(f"Grade already exists for student {student_id} in instance ({topic_id}, {index}). Skipping.", "info")
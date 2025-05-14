from flask import flash

def flash_successful_load(object_count: int, object_label: str):
    message = f"{object_count} {object_label} cargados con éxito."
    flash(message, "success")

def flash_invalid_load(object_label: str, exception: Exception):
    flash(f"Error cargando {object_label}: {str(exception)}", "danger")

# Created to handle grades, which is a special case
def flash_invalid_grades(parsed_data: list):
    for entry in parsed_data:
        reason = entry.get("__reason__")
        topic_id = entry.get("topic_id")
        index = entry.get("instance_index")
        student_id = entry.get("student_id")

        if reason == "missing_eval_instance":
            flash(f"No hay EvaluationInstance encontrado para topic ID {topic_id} e índice {index}. Saltando.", "warning")

        elif reason == "grade_exists":
            flash(f"Nota ya existe para alumno {student_id} en instancia ({topic_id}, {index}). Saltando.", "info")
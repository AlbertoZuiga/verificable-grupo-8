from app.models import Evaluation, EvaluationInstance


def get_section_id_from_evaluation_instance(evaluation_instance_id):
    # Obtener la instancia de la evaluación usando el ID
    evaluation_instance = EvaluationInstance.query.get_or_404(evaluation_instance_id)

    # Obtener el ID de la evaluación vinculada
    evaluation_id = evaluation_instance.evaluation_id

    # Obtener la sección de la evaluación
    section = Evaluation.query.get_or_404(evaluation_id).section

    # Devolver el ID de la sección
    return section.id

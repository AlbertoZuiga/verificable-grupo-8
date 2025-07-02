from app.models.evaluation import Evaluation
from app.models.evaluation_instance import EvaluationInstance
from app.models.student_evaluation_instance import StudentEvaluationInstance
from app.models.student_section import StudentSection


def get_section_id(evaluation_id):
    section = Evaluation.query.get_or_404(evaluation_id).section
    return section.id


def get_evaluation_instance_with_students_and_grades(evaluation_instance_id):
    evaluation_instance = EvaluationInstance.query.get_or_404(evaluation_instance_id)

    section_id = evaluation_instance.evaluation.section.id
    student_sections = StudentSection.query.filter_by(section_id=section_id).all()
    students = [student_section.student for student_section in student_sections]

    student_evaluation_instances = StudentEvaluationInstance.query.filter_by(
        evaluation_instance_id=evaluation_instance_id
    ).all()
    student_grades = {
        instance.student_id: instance.grade for instance in student_evaluation_instances
    }

    return evaluation_instance, students, student_grades

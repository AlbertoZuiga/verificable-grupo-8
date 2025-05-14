from app import kanvas_db
from app.models import EvaluationInstance, StudentSection, StudentEvaluationInstance, Evaluation


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


def get_evaluation_instance_and_student(evaluation_instance_id, student_id):
    evaluation_instance = EvaluationInstance.query.get_or_404(evaluation_instance_id)
    student = next((s for s in evaluation_instance.evaluation.section.students if s.id == student_id), None)
    return evaluation_instance, student


def get_student_grade_instance(evaluation_instance_id, student_id):
    return StudentEvaluationInstance.query.filter_by(
        evaluation_instance_id=evaluation_instance_id,
        student_id=student_id
    ).first()


def save_student_grade(evaluation_instance_id, student_id, grade_value):
    student_grade = get_student_grade_instance(evaluation_instance_id, student_id)

    if student_grade:
        student_grade.grade = grade_value
    else:
        student_grade = StudentEvaluationInstance(
            student_id=student_id,
            evaluation_instance_id=evaluation_instance_id,
            grade=grade_value
        )
        kanvas_db.session.add(student_grade)

    kanvas_db.session.commit()

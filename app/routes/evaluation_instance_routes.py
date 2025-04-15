from flask import Blueprint, render_template, request, redirect, url_for
from app import kanvas_db
from app.models.evaluation_instance import EvaluationInstance
from app.models.evaluation import Evaluation
from app.models.user_evaluation_instance import UserEvaluationInstance
from app.models.user_section import UserSection, SectionRole
from app.models.user import User

evaluation_instance_bp = Blueprint('evaluation_instance', __name__, url_prefix='/evaluation_instances')

@evaluation_instance_bp.route('/')
def index():
    evaluation_instances = EvaluationInstance.query.all()
    return render_template('evaluation_instances/index.html', evaluation_instances=evaluation_instances)

@evaluation_instance_bp.route('/<int:id>')
def show(id):
    evaluation_instance = EvaluationInstance.query.get_or_404(id)

    section_id = evaluation_instance.evaluation.section.id
    student_ids = kanvas_db.session.query(UserSection.user_id).filter_by(section_id=section_id, role=SectionRole.STUDENT).subquery()
    users = User.query.filter(User.id.in_(student_ids)).all()
    
    user_evaluation_instances = UserEvaluationInstance.query.filter_by(evaluation_instance_id=id).all()
    user_grades = {uei.user_id: uei for uei in user_evaluation_instances}

    return render_template('evaluation_instances/show.html', evaluation_instance=evaluation_instance, users=users, user_grades=user_grades)

@evaluation_instance_bp.route('/create', methods=['GET', 'POST'])
def create():
    if request.method == 'POST':
        title = request.form['title']
        instance_weighing = request.form['instance_weighing']
        optional = request.form.get("optional") == "on"
        evaluation_id = request.form['evaluation_id']
        
        if Evaluation.query.get(evaluation_id) is None:
            return "Invalid evaluation ID", 400
        
        evaluation_instance = EvaluationInstance(title=title, instance_weighing=instance_weighing, optional=optional, evaluation_id=evaluation_id)

        try:
            kanvas_db.session.add(evaluation_instance)
            kanvas_db.session.commit()
            return redirect(url_for('evaluation_instance.show', id=evaluation_instance.id))
        except Exception as e:
            kanvas_db.session.rollback()
            print(f"Error creating evaluation_instance: {e}")
    
    evaluations = Evaluation.query.all()
    return render_template('evaluation_instances/create.html', evaluations=evaluations)

@evaluation_instance_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    evaluation_instance = EvaluationInstance.query.get_or_404(id)
    
    if request.method == 'POST':
        evaluation_instance.title = request.form['title']
        evaluation_instance.instance_weighing = request.form['instance_weighing']
        evaluation_instance.optional = request.form.get("optional") == "on"
        evaluation_id = request.form['evaluation_id']
        
        if Evaluation.query.get(evaluation_id) is None:
            return "Invalid evaluation ID", 400
        
        evaluation_instance.evaluation_id = evaluation_id

        try:
            kanvas_db.session.commit()
            return redirect(url_for('evaluation_instance.show', id=evaluation_instance.id))
        except Exception as e:
            kanvas_db.session.rollback()
            print(f"Error updating evaluation_instance: {e}")
    
    evaluations = Evaluation.query.all()
    return render_template('evaluation_instances/edit.html', evaluation_instance=evaluation_instance, evaluations=evaluations)

@evaluation_instance_bp.route('/delete/<int:id>')
def delete(id):
    evaluation_instance = EvaluationInstance.query.get_or_404(id)
    try:
        kanvas_db.session.delete(evaluation_instance)
        kanvas_db.session.commit()
    except Exception as e:
        kanvas_db.session.rollback()
        print(f"Error deleting evaluation_instance: {e}")
    return redirect(url_for('evaluation_instance.index'))

@evaluation_instance_bp.route('/<int:evaluation_instance_id>/grade/<int:user_id>', methods=['GET', 'POST'])
def grade_user(evaluation_instance_id, user_id):
    evaluation_instance = EvaluationInstance.query.get_or_404(evaluation_instance_id)
    user = next((u for u in evaluation_instance.evaluation.section.users if u.id == user_id), None)

    if not user:
        return "Estudiante no pertenece a esta sección", 404
    
    uei = UserEvaluationInstance.query.filter(UserEvaluationInstance.user_id == user_id, UserEvaluationInstance.evaluation_instance_id == evaluation_instance_id).first()

    if request.method == 'POST':
        grade_input = request.form.get('grade')
        print(f"User ID: {user_id}")
        user_id = request.form.get('user_id')
        print(f"User ID: {user_id}")

        if grade_input and grade_input.strip() != "":
            try:
                grade_value = float(grade_input)
            except ValueError:
                return "Nota inválida", 400

            if uei:
                uei.grade = grade_value
            else:
                uei = UserEvaluationInstance(user_id=user_id, evaluation_instance_id=evaluation_instance_id, grade=grade_value)
                kanvas_db.session.add(uei)

            try:
                kanvas_db.session.commit()
                return redirect(url_for('evaluation_instance.show', id=evaluation_instance_id))
            except Exception as e:
                kanvas_db.session.rollback()
                print(f"Error al guardar la nota: {e}")

    return render_template('evaluation_instances/grade_user.html', evaluation_instance=evaluation_instance, user=user, current_grade=uei.grade if uei else None)

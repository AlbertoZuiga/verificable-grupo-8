from flask import Blueprint, render_template, request, redirect, url_for
from app import kanvas_db
from app.models.evaluation import Evaluation
from app.models.section import Section, WeighingType

evaluation_bp = Blueprint('evaluation', __name__, url_prefix='/evaluations')

@evaluation_bp.route('/')
def index():
    evaluations = Evaluation.query.all()
    return render_template('evaluations/index.html', evaluations=evaluations)

@evaluation_bp.route('/<int:id>')
def show(id):
    evaluation = Evaluation.query.get_or_404(id)
    return render_template('evaluations/show.html', evaluation=evaluation)

@evaluation_bp.route('/create', methods=['GET', 'POST'])
def create():
    if request.method == 'POST':
        title = request.form['title']
        weighing = request.form['weighing']
        weighing_system = request.form['weighing_system']
        section_id = request.form['section_id']
        
        if Section.query.get(section_id) is None:
            return "Invalid section ID", 400
        

        evaluation = Evaluation(title=title, weighing=weighing, weighing_system=weighing_system, section_id=section_id)
        try:
            kanvas_db.session.add(evaluation)
            kanvas_db.session.commit()
            return redirect(url_for('evaluation.show', id=evaluation.id))
        except Exception as e:
            kanvas_db.session.rollback()
            print(f"Error Creating evaluation: {e}")
    
    sections = Section.query.all()
    return render_template('evaluations/create.html', sections=sections, weighing_types=WeighingType)

@evaluation_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    evaluation = Evaluation.query.get_or_404(id)
    if request.method == 'POST':
        evaluation.title = request.form['title']
        evaluation.weighing = request.form['weighing']
        evaluation.weighing_system = request.form['weighing_system']
        section_id = request.form['section_id']
        
        if Section.query.get(section_id) is None:
            return "Invalid section ID", 400
        
        evaluation.section_id = section_id
        
        try:
            kanvas_db.session.commit()
            return redirect(url_for('evaluation.show', id=evaluation.id))
        except Exception as e:
            kanvas_db.session.rollback()
            print(f"Error updating evaluation: {e}")
    
    sections = Section.query.all()
    return render_template('evaluations/edit.html', evaluation=evaluation, sections=sections, weighing_types=WeighingType)

@evaluation_bp.route('/delete/<int:id>')
def delete(id):
    evaluation = Evaluation.query.get_or_404(id)
    try:
        kanvas_db.session.delete(evaluation)
        kanvas_db.session.commit()
    except Exception as e:
        kanvas_db.session.rollback()
        print(f"Error deleting evaluation: {e}")
    return redirect(url_for('evaluation.index'))

from flask import Blueprint, render_template, request, redirect, url_for
from app import db
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
        weight = request.form['weight']
        weighing_system = request.form['weighing_system']
        section_id = request.form['section_id']
        
        if Section.query.get(section_id) is None:
            return "Invalid section ID", 400
        

        evaluation = Evaluation(title=title, weight=weight, weighing_system=weighing_system, section_id=section_id)
        try:
            db.session.add(evaluation)
            db.session.commit()
            return redirect(url_for('evaluation.show', id=evaluation.id))
        except Exception as e:
            db.session.rollback()
            print(f"Error Creating evaluation: {e}")
    
    sections = Section.query.all()
    return render_template('evaluations/create.html', sections=sections, weighing_types=WeighingType)

@evaluation_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    evaluation = Evaluation.query.get_or_404(id)
    if request.method == 'POST':
        evaluation.title = request.form['title']
        evaluation.weight = request.form['weight']
        evaluation.weighing_system = request.form['weighing_system']
        section_id = request.form['section_id']
        
        if Section.query.get(section_id) is None:
            return "Invalid section ID", 400
        
        evaluation.section_id = section_id
        
        try:
            db.session.commit()
            return redirect(url_for('evaluation.show', id=evaluation.id))
        except Exception as e:
            db.session.rollback()
            print(f"Error updating evaluation: {e}")
    
    sections = Section.query.all()
    return render_template('evaluations/edit.html', evaluation=evaluation, sections=sections, weighing_types=WeighingType)

@evaluation_bp.route('/delete/<int:id>')
def delete(id):
    evaluation = Evaluation.query.get_or_404(id)
    try:
        db.session.delete(evaluation)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(f"Error deleting evaluation: {e}")
    return redirect(url_for('evaluation.index'))

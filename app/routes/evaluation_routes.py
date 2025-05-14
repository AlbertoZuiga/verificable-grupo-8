from flask import Blueprint, render_template, request, redirect, url_for, flash
from app import kanvas_db
from app.models.evaluation import Evaluation
from app.models.section import Section, WeighingType
from app.services.decorators import require_section_open
from app.services.validations import validate_section_for_evaluation

evaluation_bp = Blueprint('evaluation', __name__, url_prefix='/evaluations')

@evaluation_bp.route('/')
def index():
    evaluations = Evaluation.query.all()
    return render_template('evaluations/index.html', evaluations=evaluations)

@evaluation_bp.route('/<int:id>')
def show(id):
    evaluation = Evaluation.query.get_or_404(id)
    return render_template('evaluations/show.html', evaluation=evaluation, WeighingType=WeighingType)

@evaluation_bp.route('/<int:id>/edit_instance_weights', methods=['GET', 'POST'])
def edit_instance_weights(id):
    evaluation = Evaluation.query.get_or_404(id)

    if request.method == 'POST':
        weights = {}
        try:
            for instance in evaluation.instances:
                key = f'instance_{instance.id}'
                weights[instance.id] = float(request.form[key])
        except (ValueError, KeyError) as e:
            flash(f"Entrada inválida para los pesos: {e}", "danger")
            return redirect(url_for('evaluation.edit_instance_weights', id=evaluation.id))

        if evaluation.weighing_system == WeighingType.PERCENTAGE:
            total = sum(weights.values())
            if round(total, 2) != 100.0:
                flash("La suma de los pesos de las instancias debe ser 100 para las evaluaciones ponderadas.", "danger")
                return redirect(url_for('evaluation.edit_instance_weights', id=evaluation.id))

        for instance in evaluation.instances:
            instance.instance_weighing = weights[instance.id]

        try:
            kanvas_db.session.commit()
            flash("Pesos de instancias actualizados correctamente", "success")
            return redirect(url_for('evaluation.show', id=evaluation.id))
        except Exception as e:
            kanvas_db.session.rollback()
            flash(f"Error al guardar cambios: {e}", "danger")

    return render_template('evaluations/edit_instance_weights.html', evaluation=evaluation, WeighingType=WeighingType)

@evaluation_bp.route('/create', methods=['GET', 'POST'])
def create():
    print(request.form)    
    if request.method == 'POST':
        title = request.form['title']
        weighing_system = request.form['weighing_system']
        section_id = request.form['section_id']

        validation_error = validate_section_for_evaluation(section_id)
        if validation_error:
            return validation_error
        
        if Section.query.get(section_id) is None:
            flash("Invalid section ID", "danger")
            return redirect(url_for('evaluation_instance.create'))

        evaluation = Evaluation(title=title, weighing=0.0, weighing_system=weighing_system, section_id=section_id)
        try:
            kanvas_db.session.add(evaluation)
            kanvas_db.session.commit()
            return redirect(url_for('evaluation.show', id=evaluation.id))
        except Exception as e:
            kanvas_db.session.rollback()
            flash(f"Error Creating evaluation: {e}", "danger")

    sections = Section.query.all()
    return render_template('evaluations/create.html', sections=sections, weighing_types=WeighingType)

@evaluation_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
@require_section_open(lambda id: Evaluation.query.get_or_404(id).section)
def edit(id):
    evaluation = Evaluation.query.get_or_404(id)
    print(evaluation)
    if request.method == 'POST':
        evaluation.title = request.form['title']
        evaluation.weighing_system = request.form['weighing_system']
        section_id = request.form['section_id']
        
        if Section.query.get(section_id) is None:
            flash("Invalid section ID", "danger")
            return redirect(url_for('evaluation_instance.create'))

        evaluation.section_id = section_id

        try:
            kanvas_db.session.commit()
            return redirect(url_for('evaluation.show', id=evaluation.id))
        except Exception as e:
            kanvas_db.session.rollback()
            flash(f"Error updating evaluation: {e}", "danger")
    
    sections = Section.query.all()
    return render_template('evaluations/edit.html', evaluation=evaluation, sections=sections, weighing_types=WeighingType)

@evaluation_bp.route('/delete/<int:id>')
@require_section_open(lambda id: Evaluation.query.get_or_404(id).section)
def delete(id):
    evaluation = Evaluation.query.get_or_404(id)
    try:
        kanvas_db.session.delete(evaluation)
        kanvas_db.session.commit()
    except Exception as e:
        kanvas_db.session.rollback()
        flash("No se puede eliminar porque tiene instancias de evaluación asociadas.", "error")
        print(f"Error deleting evaluation: {e}")
        return redirect(url_for('evaluation.show', id=id))
    

    return redirect(url_for('evaluation.index'))

from flask import Blueprint, render_template, request, redirect, url_for
from app import kanvas_db
from app.models.user_section import UserSection, SectionRole
from app.models.user import User
from app.models.section import Section

user_section_bp = Blueprint('user_section', __name__, url_prefix='/sections/<int:section_id>/users')

@user_section_bp.route('/')
def index(section_id):
    section = Section.query.get_or_404(section_id)
    user_sections = UserSection.query.filter_by(section_id=section_id).all()
    return render_template('user_sections/index.html', section=section, user_sections=user_sections)

@user_section_bp.route('/add', methods=['GET', 'POST'])
def add_user(section_id):
    # Obtener la sección y los usuarios asociados a la sección
    section = Section.query.get_or_404(section_id)
    section_user_ids = [user.id for user in section.users]

    # Obtener los usuarios cuyos IDs no están en la lista de usuarios de la sección
    users = User.query.filter(User.id.notin_(section_user_ids)).all()

    if request.method == 'POST':
        user_id = request.form['user_id']
        role = request.form['role']

        if not user_id or not role:
            print("Todos los campos son obligatorios.")
        else:
            new_user_section = UserSection(user_id=user_id, section_id=section_id, role=role)
            try:
                kanvas_db.session.add(new_user_section)
                kanvas_db.session.commit()
                print("Usuario agregado exitosamente.")
                return redirect(url_for('user_section.index', section_id=section_id))
            except Exception as e:
                kanvas_db.session.rollback()
                print(f"Error al agregar usuario a la sección: {str(e)}")

    context = {
        'section': section,
        'users': users,
        'roles': SectionRole
    }
    return render_template('user_sections/add.html', **context)

@user_section_bp.route('/remove/<int:user_id>', methods=['POST'])
def remove_user(section_id, user_id):
    user_section = UserSection.query.filter_by(section_id=section_id, user_id=user_id).first_or_404()
    try:
        kanvas_db.session.delete(user_section)
        kanvas_db.session.commit()
        print("Usuario removido de la sección.")
    except Exception as e:
        kanvas_db.session.rollback()
        print(f"Error al remover usuario de la sección: {e}")
    return redirect(url_for('user_section.index', section_id=section_id))

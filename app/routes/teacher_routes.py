from flask import Blueprint, render_template, request, redirect, url_for
from app import kanvas_db
from app.models import Teacher, User

teacher_bp = Blueprint('teacher', __name__, url_prefix='/teachers')

@teacher_bp.route('/')
def index():
    teachers = Teacher.query.all()
    return render_template('teachers/index.html', teachers=teachers)

@teacher_bp.route('/<int:id>')
def show(id):
    teacher = Teacher.query.get_or_404(id)
    return render_template('teachers/show.html', teacher=teacher)

@teacher_bp.route('/create', methods=['GET', 'POST'])
def create():
    if request.method == 'POST':
        new_user = User(
            first_name=request.form['first_name'],
            last_name=request.form['last_name'],
            email=request.form['email']
        )
        new_user.set_password(request.form['password'])
        kanvas_db.session.add(new_user)
        kanvas_db.session.flush()

        new_teacher = Teacher(
            user_id=new_user.id
        )
        kanvas_db.session.add(new_teacher)
        
        kanvas_db.session.commit()
        return redirect(url_for('teacher.index'))
    return render_template('teachers/create.html')

@teacher_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    teacher = Teacher.query.get_or_404(id)
    user = teacher.user
    if request.method == 'POST':
        user.first_name = request.form['first_name']
        user.last_name = request.form['last_name']
        user.email = request.form['email']
        kanvas_db.session.commit()
        return redirect(url_for('teacher.index'))
    return render_template('teachers/edit.html', teacher=teacher)

@teacher_bp.route('/delete/<int:id>')
def delete(id):
    teacher = Teacher.query.get_or_404(id)

    kanvas_db.session.delete(teacher)
    kanvas_db.session.commit()
    return redirect(url_for('teacher.index'))

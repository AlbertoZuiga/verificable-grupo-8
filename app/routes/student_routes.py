from flask import Blueprint, render_template, request, redirect, url_for
from app import kanvas_db
from app.models import Student, User

student_bp = Blueprint('student', __name__, url_prefix='/students')

@student_bp.route('/')
def index():
    students = Student.query.all()
    return render_template('students/index.html', students=students)

@student_bp.route('/<int:id>')
def show(id):
    student = Student.query.get_or_404(id)
    return render_template('students/show.html', student=student)

@student_bp.route('/create', methods=['GET', 'POST'])
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

        new_student = Student(
            user_id=new_user.id,
            university_entry_year=request.form['university_entry_year']
        )
        kanvas_db.session.add(new_student)
        
        kanvas_db.session.commit()
        return redirect(url_for('student.index'))
    return render_template('students/create.html')

@student_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    student = Student.query.get_or_404(id)
    user = student.user
    if request.method == 'POST':
        user.first_name = request.form['first_name']
        user.last_name = request.form['last_name']
        user.email = request.form['email']
        kanvas_db.session.commit()
        return redirect(url_for('student.index'))
    return render_template('students/edit.html', student=student)

@student_bp.route('/delete/<int:id>')
def delete(id):
    student = Student.query.get_or_404(id)
    user = student.user
    kanvas_db.session.delete(student)
    kanvas_db.session.delete(user)
    kanvas_db.session.commit()
    return redirect(url_for('student.index'))

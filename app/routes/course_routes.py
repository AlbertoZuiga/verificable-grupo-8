from flask import Blueprint, render_template, request, redirect, url_for
from app import db
from app.models.course import Course

course_bp = Blueprint('course', __name__, url_prefix='/courses')

@course_bp.route('/')
def index():
    courses = Course.query.all()
    return render_template('courses/index.html', courses=courses)

@course_bp.route('/<int:id>')
def show(id):
    course = Course.query.get_or_404(id)
    return render_template('courses/show.html', course=course)

def index():
    courses = Course.query.all()
    return render_template('courses/index.html', courses=courses)

@course_bp.route('/create', methods=['GET', 'POST'])
def create():
    if request.method == 'POST':
        title = request.form['title']
        new_course = Course(title=title)
        db.session.add(new_course)
        db.session.commit()
        return redirect(url_for('course.index'))
    return render_template('courses/create.html')

@course_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    course = Course.query.get_or_404(id)
    if request.method == 'POST':
        course.title = request.form['title']
        db.session.commit()
        return redirect(url_for('course.index'))
    return render_template('courses/edit.html', course=course)

@course_bp.route('/delete/<int:id>')
def delete(id):
    course = Course.query.get_or_404(id)
    try:
        db.session.delete(course)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(f"Error deleting course: {e}")
    return redirect(url_for('course.index'))

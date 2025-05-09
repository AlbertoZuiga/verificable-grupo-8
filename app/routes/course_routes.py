from flask import Blueprint, render_template, request, redirect, url_for
from app import kanvas_db
from app.models.course import Course
from app.services.course_service import get_course_and_other_courses

course_bp = Blueprint('course', __name__, url_prefix='/courses')

@course_bp.route('/')
def index():
    courses = Course.query.all()
    return render_template('courses/index.html', courses=courses)

@course_bp.route('/<int:id>')
def show(id):
    course, courses = get_course_and_other_courses(id)
    return render_template('courses/show.html', course=course, courses=courses)

@course_bp.route('/create', methods=['GET', 'POST'])
def create():
    if request.method == 'POST':
        title = request.form['title']
        code = request.form['code']
        credits = int(request.form['credits'])
        if Course.query.filter_by(title=title).first():
            return render_template('courses/create.html', error="Ya existe un curso con ese título.")

        new_course = Course(title=title, code=code, credits=credits)
        kanvas_db.session.add(new_course)
        kanvas_db.session.commit()
        return redirect(url_for('course.index'))
    return render_template('courses/create.html')

@course_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    course = Course.query.get_or_404(id)
    if request.method == 'POST':
        course.title = request.form['title']
        course.code = request.form['code']
        course.credits = int(request.form['credits'])
        kanvas_db.session.commit()
        return redirect(url_for('course.index'))
    return render_template('courses/edit.html', course=course)

@course_bp.route('/delete/<int:id>')
def delete(id):
    course = Course.query.get_or_404(id)
    try:
        kanvas_db.session.delete(course)
        kanvas_db.session.commit()
    except Exception as e:
        kanvas_db.session.rollback()
        print(f"Error deleting course: {e}")
    return redirect(url_for('course.index'))

from flask import Blueprint, render_template, request, redirect, url_for, flash
from app import kanvas_db
from app.models.course import Course
from app.services.course_service import get_course_and_other_courses
from app.forms.course_forms import CourseForm

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
    form = CourseForm()
    if form.validate_on_submit():
        title = form.title.data
        code = form.code.data
        credits = form.credits.data

        if Course.query.filter_by(title=title).first():
            flash("Ya existe un curso con ese título.", 'danger')
            return render_template('courses/create.html', form=form)

        if Course.query.filter_by(code=code).first():
            flash("Ya existe un curso con ese codigo.", 'danger')
            return render_template('courses/create.html', form=form)

        new_course = Course(title=title, code=code, credits=credits)
        kanvas_db.session.add(new_course)
        kanvas_db.session.commit()
        flash("Instancia del curso creada exitosamente.", "success")
        return redirect(url_for('course.show', id=new_course.id))

    return render_template('courses/create.html', form=form)

@course_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    course = Course.query.get_or_404(id)
    form = CourseForm(obj=course)
    if form.validate_on_submit():
        title = form.title.data
        code = form.code.data
        credits = form.credits.data

        existing_course = Course.query.filter_by(title=title)
        if existing_course and existing_course.id != id:
            flash("Ya existe un curso con ese título.", 'danger')
            return render_template('courses/create.html', form=form, course=course)
        
        existing_course = Course.query.filter_by(code=code)
        if existing_course and existing_course.id != id:
            flash("Ya existe un curso con ese codigo.", 'danger')
            return render_template('courses/create.html', form=form, course=course)
        
        course.title = title
        course.code = code
        course.credits = credits
        
        kanvas_db.session.commit()
        flash("Instancia del curso actualizada exitosamente.", "success")
        return redirect(url_for('course.show', id=course.id))

    return render_template('courses/edit.html', form=form, course=course)

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

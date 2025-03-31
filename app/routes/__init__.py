from flask import Blueprint, render_template

main_routes = Blueprint('main', __name__)

@main_routes.route('/')
def index():
    return render_template('index.html')

""" @main_routes.route('/courses')
def courses():
    courses_list = Course.query.all()
    if not courses_list:
        return render_template('courses.html', courses=[], message="No courses available.")
    return render_template('courses.html', courses=courses_list)
 """
from app.routes.course_routes import course_bp

blueprints = [main_routes, course_bp]
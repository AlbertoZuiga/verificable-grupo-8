from flask import Blueprint, render_template
from models import Course

main_routes = Blueprint('main', __name__)

def init_app(app):
    app.register_blueprint(main_routes)

@main_routes.route('/')
def index():
    return render_template('index.html')

@main_routes.route('/courses')
def courses():
    courses_list = Course.query.all()
    if not courses_list:
        return render_template('courses.html', courses=[], message="No courses available.")
    return render_template('courses.html', courses=courses_list)

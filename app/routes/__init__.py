from flask import Blueprint, render_template

main_routes = Blueprint('main', __name__)

@main_routes.route('/')
def index():
    return render_template('index.html')

from app.routes.course_routes import course_bp
from app.routes.course_instance_routes import course_instance_bp
from app.routes.section_routes import section_bp
from app.routes.requisite_routes import requisite_bp

blueprints = [main_routes, course_bp, course_instance_bp, section_bp, requisite_bp]
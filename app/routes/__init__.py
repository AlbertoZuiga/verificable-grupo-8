from app.routes.main_routes import main_bp
from app.routes.course_routes import course_bp
from app.routes.course_instance_routes import course_instance_bp
from app.routes.section_routes import section_bp
from app.routes.requisite_routes import requisite_bp
from app.routes.evaluation_routes import evaluation_bp
from app.routes.evaluation_instance_routes import evaluation_instance_bp
from app.routes.auth_routes import auth_bp
from app.routes.user_routes import user_bp
from app.routes.user_section_routes import user_section_bp

blueprints = [main_bp, course_bp, course_instance_bp, section_bp, requisite_bp, evaluation_bp, evaluation_instance_bp, auth_bp, user_bp, user_section_bp]
from app.routes.auth_routes import auth_bp
from app.routes.classroom_routes import classroom_bp
from app.routes.course_instance_routes import course_instance_bp
from app.routes.course_routes import course_bp
from app.routes.evaluation_instance_routes import evaluation_instance_bp
from app.routes.evaluation_routes import evaluation_bp
from app.routes.grade_routes import grade_bp
from app.routes.load_json_routes import load_json_bp
from app.routes.main_routes import main_bp
from app.routes.requisite_routes import requisite_bp
from app.routes.schedule_routes import schedule_bp
from app.routes.section_routes import section_bp
from app.routes.student_routes import student_bp
from app.routes.student_section_routes import student_section_bp
from app.routes.teacher_routes import teacher_bp
from app.routes.user_routes import user_bp

blueprints = [
    main_bp,
    course_bp,
    course_instance_bp,
    section_bp,
    requisite_bp,
    evaluation_bp,
    evaluation_instance_bp,
    auth_bp,
    user_bp,
    student_section_bp,
    teacher_bp,
    student_bp,
    load_json_bp,
    classroom_bp,
    schedule_bp,
    grade_bp,
]

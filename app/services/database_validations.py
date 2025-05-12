from app.models import Classroom, User, Student

def classroom_exists(classroom_id):
    return Classroom.query.filter_by(id=classroom_id).first() is not None

def user_exists(email: str) -> bool:
    return User.query.filter_by(email=email).first() is not None

def student_exists(student_id: int) -> bool:
    return Student.query.filter_by(id=student_id).first() is not None
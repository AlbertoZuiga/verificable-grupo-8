from app import kanvas_db  

class CourseGrade(kanvas_db.Model):
    __tablename__ = 'course_grades'

    id = kanvas_db.Column(kanvas_db.Integer, primary_key=True)
    user_id = kanvas_db.Column(kanvas_db.Integer, kanvas_db.ForeignKey('users.id'), nullable=False)
    course_id = kanvas_db.Column(kanvas_db.Integer, kanvas_db.ForeignKey('courses.id'), nullable=False)
    grade = kanvas_db.Column(kanvas_db.Float, nullable=False)

    user = kanvas_db.relationship('User', backref='course_grades')

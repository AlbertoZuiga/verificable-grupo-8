from app import db
from app.models.course import Course
from sqlalchemy import CheckConstraint
from enum import Enum

class SemesterEnum(Enum):
    FIRST = 1
    SECOND = 2

class CourseInstance(db.Model):
    __tablename__ = 'course_instances'

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False, index=True)
    course = db.relationship('Course', backref='instances')
    year = db.Column(db.Integer, nullable=False, index=True)
    semester = db.Column(db.Integer, nullable=False)

    __table_args__ = (CheckConstraint('semester IN (1, 2)', name='valid_semester'),)

    def __repr__(self):
        return f"<CourseInstance id={self.id}, course_id={self.course_id}, year={self.year}, semester={self.semester}>"

    @staticmethod
    def is_valid_semester(semester):
        return semester in {SemesterEnum.FIRST.value, SemesterEnum.SECOND.value}

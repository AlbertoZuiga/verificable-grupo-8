from app import db
from sqlalchemy import CheckConstraint
from enum import Enum

class Semester(Enum):
    FIRST = 1
    SECOND = 2
    
    def __str__(self):
        return str(self.value)

class CourseInstance(db.Model):
    __tablename__ = 'course_instances'

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False, index=True)
    course = db.relationship('Course', backref='instances')
    year = db.Column(db.Integer, nullable=False, index=True)
    semester = db.Column(db.Enum(Semester), nullable=False)

    def __repr__(self):
        return f"<CourseInstance id={self.id}, course_id={self.course_id}, year={self.year}, semester={self.semester}>"
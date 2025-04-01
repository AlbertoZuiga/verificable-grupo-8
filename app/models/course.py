from app import db

class Course(db.Model):
    __tablename__ = 'courses'

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    title = db.Column(db.String(100), nullable=False, unique=True)

    prerequisites = db.relationship('Requisite', foreign_keys='Requisite.course_id', back_populates='course', overlaps="course_requisite,requisites_as_main")
    requisites_as_main = db.relationship('Requisite', foreign_keys='Requisite.course_requisite_id', back_populates='course_requisite', overlaps="course,prerequisites")

    def __repr__(self):
        return f"<Course id={self.id}, title={self.title}>"

from app import kanvas_db

class Course(kanvas_db.Model):
    __tablename__ = 'courses'

    id = kanvas_db.Column(kanvas_db.Integer, primary_key=True, nullable=False)
    title = kanvas_db.Column(kanvas_db.String(60), nullable=False, unique=True)
    code = kanvas_db.Column(kanvas_db.String(15), nullable=False, unique=True)
    credits = kanvas_db.Column(kanvas_db.Integer, nullable=False)

    prerequisites = kanvas_db.relationship('Requisite', foreign_keys='Requisite.course_id', back_populates='course', overlaps="course_requisite,requisites_as_main", cascade='all, delete-orphan')
    requisites_as_main = kanvas_db.relationship('Requisite', foreign_keys='Requisite.course_requisite_id', back_populates='course_requisite', overlaps="course,prerequisites", cascade='all, delete-orphan')

    instances = kanvas_db.relationship('CourseInstance', back_populates='course', cascade='all, delete-orphan')

    def __repr__(self):
        return f"<Course id={self.id}, title={self.title}, code={self.code}, credits={self.credits}>"

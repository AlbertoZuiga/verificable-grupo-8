from app import kanvas_db

class Course(kanvas_db.Model):
    __tablename__ = 'courses'

    id = kanvas_db.Column(kanvas_db.Integer, primary_key=True, nullable=False)
    title = kanvas_db.Column(kanvas_db.String(100), nullable=False, unique=True)

    prerequisites = kanvas_db.relationship('Requisite', foreign_keys='Requisite.course_id', back_populates='course', overlaps="course_requisite,requisites_as_main")
    requisites_as_main = kanvas_db.relationship('Requisite', foreign_keys='Requisite.course_requisite_id', back_populates='course_requisite', overlaps="course,prerequisites")

    def __repr__(self):
        return f"<Course id={self.id}, title={self.title}>"

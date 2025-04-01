from app import db

class Requisite(db.Model):
    __tablename__ = 'requisites'

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    course_requisite_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)

    course = db.relationship('Course', foreign_keys=[course_id], back_populates='prerequisites', overlaps="course_requisite,requisites_as_main")
    course_requisite = db.relationship('Course', foreign_keys=[course_requisite_id], back_populates='requisites_as_main', overlaps="course,prerequisites")
    

    def __repr__(self):
        return f"<Requisite id={self.id}, course_id={self.course_id}, course_requisite_id={self.course_requisite_id}>"

from app import kanvas_db

class Student(kanvas_db.Model):
    __tablename__ = 'students'

    id = kanvas_db.Column(kanvas_db.Integer, primary_key=True, autoincrement=True)
    
    user_id = kanvas_db.Column(kanvas_db.Integer, kanvas_db.ForeignKey("users.id"), unique=True, nullable=False)
    user = kanvas_db.relationship("User", back_populates="student")

    university_entry_year = kanvas_db.Column(kanvas_db.Integer, nullable=False)
    
    sections = kanvas_db.relationship('Section',  secondary='student_sections',  back_populates='students', viewonly=True)

    section_associations = kanvas_db.relationship('StudentSection',  back_populates='student', cascade='all, delete-orphan', passive_deletes=False)

    student_evaluation_instances = kanvas_db.relationship('StudentEvaluationInstance', back_populates='student', cascade='all, delete-orphan')
    evaluation_instances = kanvas_db.relationship('EvaluationInstance', secondary='student_evaluation_instances', viewonly=True, back_populates='students')

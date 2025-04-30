from app import kanvas_db
from app.models import User

class Student(User):
    __tablename__ = 'students'
    id = kanvas_db.Column(kanvas_db.Integer, kanvas_db.ForeignKey('users.id'), primary_key=True)
    university_entry_year = kanvas_db.Column(kanvas_db.Integer, nullable=False)
    
    __mapper_args__ = {'polymorphic_identity': 'student'}
    
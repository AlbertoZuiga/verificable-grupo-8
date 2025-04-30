from app import kanvas_db
from app.models.user import User

class Teacher(User):
    __tablename__ = 'teachers'
    id = kanvas_db.Column(kanvas_db.Integer, kanvas_db.ForeignKey('users.id'), primary_key=True)
    __mapper_args__ = {'polymorphic_identity': 'teacher'}
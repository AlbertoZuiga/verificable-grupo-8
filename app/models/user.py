from app import kanvas_db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

class User(UserMixin, kanvas_db.Model):
    __tablename__ = 'users'

    id = kanvas_db.Column(kanvas_db.Integer, primary_key=True, nullable=False)
    email = kanvas_db.Column(kanvas_db.String(120), nullable=False, unique=True, index=True)
    password_hash = kanvas_db.Column(kanvas_db.String(256), nullable=False)
    first_name = kanvas_db.Column(kanvas_db.String(100), nullable=False)
    last_name = kanvas_db.Column(kanvas_db.String(100), nullable=False)
    university_entry_year = kanvas_db.Column(kanvas_db.Integer, nullable=False)

    user_sections = kanvas_db.relationship('UserSection', back_populates='user')
    sections = kanvas_db.relationship('Section', secondary='user_sections', viewonly=True, back_populates='users')
    
    user_evaluation_instances = kanvas_db.relationship('UserEvaluationInstance', back_populates='user')
    evaluation_instances = kanvas_db.relationship('EvaluationInstance', secondary='user_evaluation_instances', viewonly=True, back_populates='users')

    def __repr__(self):
        return f"<User id={self.id}, name={self.first_name} {self.last_name}, email={self.email}>"

    def set_password(self, password):
        self.password_hash = generate_password_hash(password, method='pbkdf2:sha256')

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

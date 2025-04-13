from app import kanvas_db  
from enum import Enum

class SectionRole(Enum):
    ESTUDIANTE = "ESTUDIANTE"
    AYUDANTE = "AYUDANTE"
    PROFESOR = "PROFESOR"
    
    def __str__(self):
        return self.value

class UserSection(kanvas_db.Model):
    __tablename__ = 'user_sections'

    section_id = kanvas_db.Column(kanvas_db.Integer, kanvas_db.ForeignKey('sections.id'), primary_key=True)
    user_id = kanvas_db.Column(kanvas_db.Integer, kanvas_db.ForeignKey('users.id'), primary_key=True)
    role = kanvas_db.Column(kanvas_db.Enum(SectionRole, name="section_role_enum"), nullable=False)

    user = kanvas_db.relationship('User', back_populates='user_sections')
    section = kanvas_db.relationship('Section', back_populates='user_sections')

    def __repr__(self):
        return f"<UserSection user_id={self.user_id} section_id={self.section_id} role={self.role}>"

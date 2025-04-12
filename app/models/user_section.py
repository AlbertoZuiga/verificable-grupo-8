from app import kanvas_db  

class UserSection(kanvas_db.Model):
    __tablename__ = 'user_sections'

    section_id = kanvas_db.Column(kanvas_db.Integer, kanvas_db.ForeignKey('sections.id'), primary_key=True)
    user_id = kanvas_db.Column(kanvas_db.Integer, kanvas_db.ForeignKey('users.id'), primary_key=True)
    role = kanvas_db.Column(kanvas_db.String(50), nullable=False)

    user = kanvas_db.relationship('User', backref='user_sections')
    section = kanvas_db.relationship('Section', backref='user_sections')

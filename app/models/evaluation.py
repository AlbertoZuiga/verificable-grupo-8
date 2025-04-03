from app import db
from app.models.section import WeighingType

class Evaluation(db.Model):
    __tablename__ = 'evaluations'

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    
    section_id = db.Column(db.Integer, db.ForeignKey('sections.id'), nullable=False, index=True)
    section = db.relationship('Section', backref='evaluations')
    
    title = db.Column(db.String(100), nullable=False)
    weighing = db.Column(db.Integer, nullable=False)
    weighing_system = db.Column(db.Enum(WeighingType), nullable=False)

    def __repr__(self):
        return f"<Evaluation id={self.id}, title={self.title}, weighing_system={self.weighing_system}>"

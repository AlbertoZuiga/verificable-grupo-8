from app import kanvas_db
from app.models.section import WeighingType

class Evaluation(kanvas_db.Model):
    __tablename__ = 'evaluations'

    id = kanvas_db.Column(kanvas_db.Integer, primary_key=True, nullable=False)
    
    section_id = kanvas_db.Column(kanvas_db.Integer, kanvas_db.ForeignKey('sections.id'), nullable=False, index=True)
    section = kanvas_db.relationship('Section', backref='evaluations')
    
    title = kanvas_db.Column(kanvas_db.String(100), nullable=False)
    weighing = kanvas_db.Column(kanvas_db.Integer, nullable=False)
    weighing_system = kanvas_db.Column(kanvas_db.Enum(WeighingType), nullable=False)

    def __repr__(self):
        return f"<Evaluation id={self.id}, title={self.title}, weighing_system={self.weighing_system}>"

    @property
    def total_weighing(self):
        return sum(instance.instance_weighing for instance in self.instances)
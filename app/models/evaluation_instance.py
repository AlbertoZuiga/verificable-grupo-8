from app import db

class EvaluationInstance(db.Model):
    __tablename__ = 'evaluation_instances'

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    
    evaluation_id = db.Column(db.Integer, db.ForeignKey('evaluations.id'), nullable=False, index=True)
    evaluation = db.relationship('Evaluation', backref='instances')
    
    title = db.Column(db.String(100), nullable=False)
    instance_weighing = db.Column(db.Integer, nullable=False)
    optional = db.Column(db.Boolean, default=False, nullable=False)

    def __repr__(self):
        return f"<EvaluationInstance id={self.id}, title={self.title}, weighing={self.weighing}>"

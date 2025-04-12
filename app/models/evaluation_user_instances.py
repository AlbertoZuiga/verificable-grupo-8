from app import kanvas_db  

class EvaluationUserInstance(kanvas_db.Model):
    __tablename__ = 'evaluation_user_instances'

    evaluation_instance_id = kanvas_db.Column(kanvas_db.Integer, kanvas_db.ForeignKey('evaluation_instances.id'), primary_key=True)
    user_id = kanvas_db.Column(kanvas_db.Integer, kanvas_db.ForeignKey('users.id'), primary_key=True)
    grade = kanvas_db.Column(kanvas_db.Float)

    user = kanvas_db.relationship('User', backref='evaluation_user_instances')
    evaluation_instance = kanvas_db.relationship('EvaluationInstance', backref='evaluation_user_instances')

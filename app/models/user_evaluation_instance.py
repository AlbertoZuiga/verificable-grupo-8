from app import kanvas_db

class UserEvaluationInstance(kanvas_db.Model):
    __tablename__ = 'user_evaluation_instances'

    evaluation_instance_id = kanvas_db.Column(kanvas_db.Integer, kanvas_db.ForeignKey('evaluation_instances.id'), primary_key=True)
    user_id = kanvas_db.Column(kanvas_db.Integer, kanvas_db.ForeignKey('users.id'), primary_key=True)
    grade = kanvas_db.Column(kanvas_db.Float)

    user = kanvas_db.relationship('User', back_populates='user_evaluation_instances')
    evaluation_instance = kanvas_db.relationship('EvaluationInstance', back_populates='user_evaluation_instances')

    def __repr__(self):
        return f"<UserEvaluationInstance user_id={self.user_id} evaluation_instance_id={self.evaluation_instance_id} grade={self.grade}>"

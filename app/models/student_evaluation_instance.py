from app import kanvas_db

class StudentEvaluationInstance(kanvas_db.Model):
    __tablename__ = 'student_evaluation_instances'

    student_id = kanvas_db.Column(kanvas_db.Integer, kanvas_db.ForeignKey('students.id'), primary_key=True)
    evaluation_instance_id = kanvas_db.Column(kanvas_db.Integer, kanvas_db.ForeignKey('evaluation_instances.id'), primary_key=True)
    evaluation_id = kanvas_db.Column(kanvas_db.Integer, kanvas_db.ForeignKey('evaluations.id'), primary_key=True)

    grade = kanvas_db.Column(kanvas_db.Float)

    student = kanvas_db.relationship('Student', back_populates='student_evaluation_instances')
    evaluation_instance = kanvas_db.relationship('EvaluationInstance', back_populates='student_evaluation_instances')
    evaluation = kanvas_db.relationship('Evaluation')  

    def __repr__(self):
        return f"<StudentEvaluationInstance student_id={self.student_id} evaluation_instance_id={self.evaluation_instance_id} evaluation_id={self.evaluation_id} grade={self.grade}>"

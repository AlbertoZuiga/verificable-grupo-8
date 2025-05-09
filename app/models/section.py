from app import kanvas_db
import enum

class WeighingType(enum.Enum):
    PERCENTAGE = "Porcentaje"
    WEIGHT = "Peso"

    def __str__(self):
        return self.value

class Section(kanvas_db.Model):
    __tablename__ = 'sections'

    id = kanvas_db.Column(kanvas_db.Integer, primary_key=True, nullable=False)
    
    course_instance_id = kanvas_db.Column(kanvas_db.Integer, kanvas_db.ForeignKey('course_instances.id'), nullable=False, index=True)
    course_instance = kanvas_db.relationship('CourseInstance', backref='sections')
    
    code = kanvas_db.Column(kanvas_db.Integer, nullable=False, index=True, unique=True)
    weighing_type = kanvas_db.Column(kanvas_db.Enum(WeighingType), nullable=False)

    teacher_id = kanvas_db.Column(kanvas_db.Integer, kanvas_db.ForeignKey('teachers.id'), nullable=False, index=True)
    teacher = kanvas_db.relationship('Teacher', backref='sections')
    
    student_sections = kanvas_db.relationship('StudentSection', back_populates='section')
    students = kanvas_db.relationship('Student', secondary='student_sections', viewonly=True, back_populates='sections')

    def __repr__(self):
        return f"<Section id={self.id}, code={self.code}, weighing_type={self.weighing_type}>"
    
    @property
    def total_weighing(self):
        return sum(evaluation.weighing for evaluation in self.evaluations)

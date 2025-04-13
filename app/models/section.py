from app import kanvas_db
import enum
from app.models.user_section import UserSection

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

    user_sections = kanvas_db.relationship('UserSection', back_populates='section')
    users = kanvas_db.relationship('User', secondary='user_sections', viewonly=True, back_populates='sections')

    def __repr__(self):
        return f"<Section id={self.id}, code={self.code}, weighing_type={self.weighing_type}>"
    
    @property
    def total_weighing(self):
        return sum(e.weighing for e in self.evaluations)

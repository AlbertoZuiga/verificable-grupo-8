from app import db
import enum

class WeighingType(enum.Enum):
    PERCENTAGE = "Porcentaje"
    WEIGHT = "Peso"

    def __str__(self):
        return self.value

class Section(db.Model):
    __tablename__ = 'sections'

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    course_instance_id = db.Column(db.Integer, db.ForeignKey('course_instances.id'), nullable=False, index=True)
    course_instance = db.relationship('CourseInstance', backref='sections')
    code = db.Column(db.Integer, nullable=False, index=True, unique=True)
    weighing_type = db.Column(db.Enum(WeighingType), nullable=False)

    def __repr__(self):
        return f"<Section id={self.id}, code={self.code}, weighing_type={self.weighing_type}>"

from app import db
import enum

class WeightingType(enum.Enum):
    PERCENTAGE = "Porcentaje"
    WEIGHTS = "Peso"

    def __str__(self):
        return self.name

class Section(db.Model):
    """
    Represents a section of a course instance.
    """
    __tablename__ = 'sections'

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    course_instance_id = db.Column(db.Integer, db.ForeignKey('course_instances.id'), nullable=False, index=True)
    course_instance = db.relationship('CourseInstance', backref='sections')
    code = db.Column(db.Integer, nullable=False, index=True, unique=True)
    weighting_type = db.Column(db.Enum(WeightingType), nullable=False)

    def __repr__(self):
        return f"<Section id={self.id}, code={self.code}, weighting_type={self.weighting_type}>"

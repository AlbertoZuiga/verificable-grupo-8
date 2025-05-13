from app import kanvas_db

class Classroom(kanvas_db.Model):
    __tablename__ = 'classrooms'

    id = kanvas_db.Column(kanvas_db.Integer, primary_key=True)
    name = kanvas_db.Column(kanvas_db.String(50), nullable=False, unique=True)
    capacity = kanvas_db.Column(kanvas_db.Integer, nullable=False)

    assigned_time_blocks = kanvas_db.relationship('AssignedTimeBlock', back_populates='classroom', cascade='all, delete-orphan')

    def __repr__(self):
        return f"<Classroom {self.name} ({self.capacity})>"


from app import kanvas_db as db

class Classroom(db.Model):
    __tablename__ = 'classrooms'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    capacity = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f"<Classroom {self.name} ({self.capacity})>"


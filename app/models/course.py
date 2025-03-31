from app import db

class Course(db.Model):
    __tablename__ = 'courses'

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    title = db.Column(db.String(100), nullable=False, unique=True)
    
    def __repr__(self):
        return f"<Course id={self.id}, title={self.title}>"

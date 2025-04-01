from app import db

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False, unique=True, index=True)
    university_entry_date = db.Column(db.Date, nullable=False)

    def __repr__(self):
        return f"<User id={self.id}, name={self.name}, email={self.email}>"
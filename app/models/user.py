from app import kanvas_db

class User(kanvas_db.Model):
    __tablename__ = 'users'

    id = kanvas_db.Column(kanvas_db.Integer, primary_key=True, nullable=False)
    first_name = kanvas_db.Column(kanvas_db.String(100), nullable=False)
    last_name = kanvas_db.Column(kanvas_db.String(100), nullable=False)
    email = kanvas_db.Column(kanvas_db.String(120), nullable=False, unique=True, index=True)
    university_entry_date = kanvas_db.Column(kanvas_db.Date, nullable=False)

    def __repr__(self):
        return f"<User id={self.id}, name={self.name}, email={self.email}>"
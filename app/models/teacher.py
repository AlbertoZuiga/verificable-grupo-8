from app.extensions import kanvas_db


class Teacher(kanvas_db.Model):  # type: ignore[name-defined]
    __tablename__ = "teachers"

    id = kanvas_db.Column(kanvas_db.Integer, primary_key=True, autoincrement=True)

    user_id = kanvas_db.Column(
        kanvas_db.Integer, kanvas_db.ForeignKey("users.id"), unique=True, nullable=False
    )
    user = kanvas_db.relationship("User", back_populates="teacher")

    sections = kanvas_db.relationship(
        "Section", back_populates="teacher", cascade="all, delete-orphan"
    )

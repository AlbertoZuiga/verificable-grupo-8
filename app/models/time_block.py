from app import kanvas_db


class TimeBlock(kanvas_db.Model):
    __tablename__ = "time_blocks"

    id = kanvas_db.Column(kanvas_db.Integer, primary_key=True)
    start_time = kanvas_db.Column(kanvas_db.Time, nullable=False)
    stop_time = kanvas_db.Column(kanvas_db.Time, nullable=False)
    weekday = kanvas_db.Column(kanvas_db.String(10), nullable=False)

    assigned_time_blocks = kanvas_db.relationship(
        "AssignedTimeBlock", back_populates="time_block", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<TimeBlock {self.weekday} {self.start_time}-{self.stop_time}>"

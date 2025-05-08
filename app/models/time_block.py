from app import kanvas_db as db

class TimeBlock(db.Model):
    __tablename__ = 'time_blocks'

    id = db.Column(db.Integer, primary_key=True)
    start_time = db.Column(db.Time, nullable=False)
    stop_time = db.Column(db.Time, nullable=False)
    weekday = db.Column(db.String(10), nullable=False)  # e.g. 'Monday'

    def __repr__(self):
        return f"<TimeBlock {self.weekday} {self.start_time}-{self.stop_time}>"


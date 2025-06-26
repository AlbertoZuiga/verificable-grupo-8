from app import kanvas_db


class AssignedTimeBlock(kanvas_db.Model):
    __tablename__ = "assigned_time_blocks"

    id = kanvas_db.Column(kanvas_db.Integer, primary_key=True)

    section_id = kanvas_db.Column(
        kanvas_db.Integer,
        kanvas_db.ForeignKey("sections.id", ondelete="CASCADE"),
        nullable=False,
    )
    section = kanvas_db.relationship("Section", back_populates="assigned_time_blocks")

    classroom_id = kanvas_db.Column(
        kanvas_db.Integer,
        kanvas_db.ForeignKey("classrooms.id", ondelete="CASCADE"),
        nullable=False,
    )
    classroom = kanvas_db.relationship(
        "Classroom", back_populates="assigned_time_blocks"
    )

    time_block_id = kanvas_db.Column(
        kanvas_db.Integer,
        kanvas_db.ForeignKey("time_blocks.id", ondelete="CASCADE"),
        nullable=False,
    )
    time_block = kanvas_db.relationship(
        "TimeBlock", back_populates="assigned_time_blocks"
    )

    __table_args__ = (
        kanvas_db.UniqueConstraint(
            "classroom_id", "time_block_id", name="uq_classroom_timeblock"
        ),
        kanvas_db.UniqueConstraint(
            "section_id", "time_block_id", name="uq_section_timeblock"
        ),
    )

    def __repr__(self):
        return f"<AssignedTimeBlock section={self.section_id} classroom={self.classroom_id} block={self.time_block_id}>"

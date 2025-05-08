from app import kanvas_db as db

class AssignedTimeBlock(db.Model):
    __tablename__ = 'assigned_time_blocks'

    id = db.Column(db.Integer, primary_key=True)
    section_id = db.Column(db.Integer, db.ForeignKey('sections.id'), nullable=False)
    classroom_id = db.Column(db.Integer, db.ForeignKey('classrooms.id'), nullable=False)
    time_block_id = db.Column(db.Integer, db.ForeignKey('time_blocks.id'), nullable=False)

    __table_args__ = (
        db.UniqueConstraint('classroom_id', 'time_block_id', name='uq_classroom_timeblock'),
        db.UniqueConstraint('section_id', 'time_block_id', name='uq_section_timeblock'),
    )

    section = db.relationship('Section', backref='assigned_time_blocks')
    classroom = db.relationship('Classroom', backref='assigned_time_blocks')
    time_block = db.relationship('TimeBlock', backref='assigned_time_blocks')

    def __repr__(self):
        return f"<AssignedTimeBlock section={self.section_id} classroom={self.classroom_id} block={self.time_block_id}>"
from app import kanvas_db

class StudentSection(kanvas_db.Model):
    __tablename__ = 'student_sections'

    section_id = kanvas_db.Column(kanvas_db.Integer, kanvas_db.ForeignKey('sections.id'), primary_key=True)
    student_id = kanvas_db.Column(kanvas_db.Integer, kanvas_db.ForeignKey('students.id'), primary_key=True)

    student = kanvas_db.relationship('Student', back_populates='student_sections')
    section = kanvas_db.relationship('Section', back_populates='student_sections')

    def __repr__(self):
        return f"<StudentSection student_id={self.student_id} section_id={self.section_id}>"

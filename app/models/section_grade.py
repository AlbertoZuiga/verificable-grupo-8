from app import kanvas_db


class SectionGrade(kanvas_db.Model):
    __tablename__ = "section_grades"

    id = kanvas_db.Column(kanvas_db.Integer, primary_key=True)
    student_id = kanvas_db.Column(
        kanvas_db.Integer, kanvas_db.ForeignKey("students.id"), nullable=False
    )
    section_id = kanvas_db.Column(
        kanvas_db.Integer, kanvas_db.ForeignKey("sections.id"), nullable=False
    )
    grade = kanvas_db.Column(kanvas_db.Float, nullable=False)

    __table_args__ = (
        kanvas_db.UniqueConstraint(
            "student_id", "section_id", name="unique_student_section"
        ),
    )
    student = kanvas_db.relationship("Student", backref="grades")
    section = kanvas_db.relationship("Section", backref="grades")

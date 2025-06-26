from app import kanvas_db


class StudentSection(kanvas_db.Model):  # type: ignore[name-defined]
    __tablename__ = "student_sections"

    section_id = kanvas_db.Column(
        kanvas_db.Integer,
        kanvas_db.ForeignKey("sections.id", ondelete="CASCADE"),
        primary_key=True,
    )
    section = kanvas_db.relationship(
        "Section",
        back_populates="student_associations",
        overlaps="students,student_associations",
    )

    student_id = kanvas_db.Column(
        kanvas_db.Integer,
        kanvas_db.ForeignKey("students.id", ondelete="CASCADE"),
        primary_key=True,
    )
    student = kanvas_db.relationship(
        "Student",
        back_populates="section_associations",
        overlaps="sections,section_associations",
    )

    def __repr__(self):
        return f"<StudentSection student_id={self.student_id} section_id={self.section_id}>"

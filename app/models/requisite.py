from app.extensions import kanvas_db


class Requisite(kanvas_db.Model):  # type: ignore[name-defined]
    __tablename__ = "requisites"

    id = kanvas_db.Column(kanvas_db.Integer, primary_key=True, nullable=False)
    course_id = kanvas_db.Column(
        kanvas_db.Integer, kanvas_db.ForeignKey("courses.id"), nullable=False
    )
    course_requisite_id = kanvas_db.Column(
        kanvas_db.Integer, kanvas_db.ForeignKey("courses.id"), nullable=False
    )

    __table_args__ = (
        kanvas_db.UniqueConstraint("course_id", "course_requisite_id", name="uq_course_requisite"),
    )

    course = kanvas_db.relationship(
        "Course",
        foreign_keys=[course_id],
        back_populates="prerequisites",
        overlaps="course_requisite,requisites_as_main",
    )
    course_requisite = kanvas_db.relationship(
        "Course",
        foreign_keys=[course_requisite_id],
        back_populates="requisites_as_main",
        overlaps="course,prerequisites",
    )

    def __repr__(self):
        return f"<Requisite id={self.id},\
                            course_id={self.course_id},\
                            course_requisite_id={self.course_requisite_id}>"

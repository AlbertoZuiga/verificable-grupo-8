from enum import Enum

from app import kanvas_db


class Semester(Enum):
    FIRST = 1
    SECOND = 2

    def __str__(self):
        return str(self.value)


class CourseInstance(kanvas_db.Model):  # type: ignore[name-defined]
    __tablename__ = "course_instances"

    id = kanvas_db.Column(kanvas_db.Integer, primary_key=True, nullable=False)

    course_id = kanvas_db.Column(
        kanvas_db.Integer,
        kanvas_db.ForeignKey("courses.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    course = kanvas_db.relationship("Course", back_populates="instances")

    year = kanvas_db.Column(kanvas_db.Integer, nullable=False, index=True)
    semester = kanvas_db.Column(kanvas_db.Enum(Semester), nullable=False)

    sections = kanvas_db.relationship(
        "Section", back_populates="course_instance", cascade="all, delete-orphan"
    )

    __table_args__ = (
        kanvas_db.UniqueConstraint(
            "course_id", "year", "semester", name="unique_course_year_semester"
        ),
    )

    def __repr__(self):
        return f"<CourseInstance id={self.id}, course_id={self.course_id}, year={self.year}, semester={self.semester}>"

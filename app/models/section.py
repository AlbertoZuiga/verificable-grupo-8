import enum

from app.extensions import kanvas_db

DELETION_MODE = "all, delete-orphan"


class WeighingType(enum.Enum):
    PERCENTAGE = "Porcentaje"
    WEIGHT = "Peso"

    def __str__(self):
        return self.value


class Section(kanvas_db.Model):  # type: ignore[name-defined]
    __tablename__ = "sections"

    id = kanvas_db.Column(kanvas_db.Integer, primary_key=True, nullable=False)

    course_instance_id = kanvas_db.Column(
        kanvas_db.Integer,
        kanvas_db.ForeignKey("course_instances.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    course_instance = kanvas_db.relationship("CourseInstance", back_populates="sections")

    code = kanvas_db.Column(kanvas_db.Integer, nullable=False, index=True, unique=True)
    weighing_type = kanvas_db.Column(kanvas_db.Enum(WeighingType), nullable=False)

    teacher_id = kanvas_db.Column(
        kanvas_db.Integer,
        kanvas_db.ForeignKey("teachers.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    teacher = kanvas_db.relationship("Teacher", back_populates="sections")

    students = kanvas_db.relationship(
        "Student",
        secondary="student_sections",
        back_populates="sections",
        viewonly=True,
    )

    student_associations = kanvas_db.relationship(
        "StudentSection",
        back_populates="section",
        cascade=DELETION_MODE,
        passive_deletes=False,
    )

    assigned_time_blocks = kanvas_db.relationship(
        "AssignedTimeBlock", back_populates="section", cascade=DELETION_MODE
    )
    evaluations = kanvas_db.relationship(
        "Evaluation", back_populates="section", cascade=DELETION_MODE
    )
    closed = kanvas_db.Column(kanvas_db.Boolean, default=False)

    __table_args__ = (
        kanvas_db.UniqueConstraint(
            "course_instance_id",
            "teacher_id",
            "code",
            name="unique_course_instance_teacher_code",
        ),
    )

    def __repr__(self):
        return f"<Section id={self.id}, code={self.code}, weighing_type={self.weighing_type}>"

    @property
    def total_weighing(self):
        return sum(evaluation.weighing for evaluation in self.evaluations)

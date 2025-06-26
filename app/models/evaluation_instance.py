from app import kanvas_db


class EvaluationInstance(kanvas_db.Model):  # type: ignore[name-defined]
    __tablename__ = "evaluation_instances"

    id = kanvas_db.Column(kanvas_db.Integer, primary_key=True, nullable=False)

    index_in_evaluation = kanvas_db.Column(kanvas_db.Integer, nullable=False)

    evaluation_id = kanvas_db.Column(
        kanvas_db.Integer,
        kanvas_db.ForeignKey("evaluations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    evaluation = kanvas_db.relationship("Evaluation", back_populates="instances")

    title = kanvas_db.Column(kanvas_db.String(100), nullable=False)
    instance_weighing = kanvas_db.Column(kanvas_db.Float, nullable=False)
    optional = kanvas_db.Column(kanvas_db.Boolean, default=False, nullable=False)

    student_evaluation_instances = kanvas_db.relationship(
        "StudentEvaluationInstance",
        back_populates="evaluation_instance",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    students = kanvas_db.relationship(
        "Student",
        secondary="student_evaluation_instances",
        viewonly=True,
        back_populates="evaluation_instances",
    )

    __table_args__ = (
        kanvas_db.UniqueConstraint(
            "evaluation_id", "title", name="unique_evaluation_title"
        ),
    )

    def __repr__(self):
        return f"<EvaluationInstance id={self.id}, title={self.title}, weighing={self.instance_weighing}>"

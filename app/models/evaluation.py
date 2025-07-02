from app.extensions import kanvas_db
from app.models.section import WeighingType


class Evaluation(kanvas_db.Model):  # type: ignore[name-defined]
    __tablename__ = "evaluations"

    id = kanvas_db.Column(kanvas_db.Integer, primary_key=True, nullable=False)

    section_id = kanvas_db.Column(
        kanvas_db.Integer,
        kanvas_db.ForeignKey("sections.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    section = kanvas_db.relationship("Section", back_populates="evaluations")

    title = kanvas_db.Column(kanvas_db.String(100), nullable=False)
    weighing = kanvas_db.Column(kanvas_db.Float, nullable=False, default=0.0)
    weighing_system = kanvas_db.Column(kanvas_db.Enum(WeighingType), nullable=False)

    instances = kanvas_db.relationship(
        "EvaluationInstance", back_populates="evaluation", cascade="all, delete-orphan"
    )

    __table_args__ = (
        kanvas_db.UniqueConstraint("section_id", "title", name="unique_section_title"),
    )

    def __repr__(self):
        return (
            f"<Evaluation id={self.id}, title={self.title}, weighing_system={self.weighing_system}>"
        )

    @property
    def total_weighing(self):
        return sum(instance.instance_weighing for instance in self.instances)

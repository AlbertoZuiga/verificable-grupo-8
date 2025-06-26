from app import kanvas_db


class Course(kanvas_db.Model):  # type: ignore[name-defined]
    __tablename__ = "courses"

    id = kanvas_db.Column(kanvas_db.Integer, primary_key=True, nullable=False)
    title = kanvas_db.Column(kanvas_db.String(60), nullable=False, unique=True)
    code = kanvas_db.Column(kanvas_db.String(15), nullable=False, unique=True)
    credits = kanvas_db.Column(kanvas_db.Integer, nullable=False)

    prerequisites = kanvas_db.relationship(
        "Requisite",
        foreign_keys="Requisite.course_id",
        back_populates="course",
        overlaps="course_requisite,requisites_as_main",
        cascade="all, delete-orphan",
    )
    requisites_as_main = kanvas_db.relationship(
        "Requisite",
        foreign_keys="Requisite.course_requisite_id",
        back_populates="course_requisite",
        overlaps="course,prerequisites",
        cascade="all, delete-orphan",
    )

    instances = kanvas_db.relationship(
        "CourseInstance", back_populates="course", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return (
            f"<Course id={self.id}, title={self.title}, code={self.code}, credits={self.credits}>"
        )

    def has_cyclic_requisite(self, new_requisite_course):
        def _check_cycle(course, target_course_id, visited=None):
            if visited is None:
                visited = set()
            if course.id in visited:
                return False
            visited.add(course.id)

            if course.id == target_course_id:
                return True
            for requisite in course.prerequisites:

                if _check_cycle(requisite.course_requisite, target_course_id, visited):
                    return True
            return False

        return _check_cycle(new_requisite_course, self.id)

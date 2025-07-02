from flask import flash

from app.models.section import Section


def validate_section_for_evaluation(section_id):
    section = Section.query.get(section_id)

    if section is None:
        flash("ID de sección invalido", "danger")
        return True

    if section.closed:
        flash("Sección cerrada.", "warning")
        return True

    return None

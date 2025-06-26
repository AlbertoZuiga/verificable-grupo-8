# app/validators.py
from flask import flash, redirect, url_for

from app.models import Section


def validate_section_for_evaluation(section_id):
    section = Section.query.get_or_404(section_id)

    if section is None:
        return "Invalid section ID", 400

    if section.closed:
        flash("Sección cerrada.", "warning")
        return redirect(url_for("evaluation.create"))

    return None

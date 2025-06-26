import io

import pandas as pd
from flask import (Blueprint, flash, redirect, render_template, request,
                   send_file, url_for)

from app import kanvas_db
from app.models import AssignedTimeBlock, TimeBlock
from app.services import delete_assigned_time_blocks, generate_schedule

schedule_bp = Blueprint("schedule", __name__, url_prefix="/schedule")


def get_schedule():
    raw_schedule = fetch_assigned_time_blocks()
    return build_clean_schedule(raw_schedule)


def fetch_assigned_time_blocks():
    return (
        kanvas_db.session.query(AssignedTimeBlock)
        .join(TimeBlock, TimeBlock.id == AssignedTimeBlock.time_block_id)
        .order_by(TimeBlock.start_time)
        .all()
    )


def build_clean_schedule(schedule):
    clean_schedule = {}
    for entry in schedule:
        section_id = entry.section_id
        if section_id not in clean_schedule:
            clean_schedule[section_id] = build_schedule_entry(entry)
        else:
            clean_schedule[section_id]["stop_time"] = (
                entry.time_block.stop_time.strftime("%H:%M")
            )
    return clean_schedule


def build_schedule_entry(entry):
    return {
        "course_title": entry.section.course_instance.course.title,
        "course_code": entry.section.course_instance.course.code,
        "section_code": entry.section.code,
        "classroom": entry.classroom.name,
        "weekday": entry.time_block.weekday,
        "start_time": entry.time_block.start_time.strftime("%H:%M"),
        "stop_time": entry.time_block.stop_time.strftime("%H:%M"),
    }


@schedule_bp.route("/")
def index():
    schedule = get_schedule()
    return render_template("schedule/index.html", schedule=schedule)


@schedule_bp.route("/generate")
def generate():
    try:
        delete_assigned_time_blocks()
        generate_schedule()
        flash("Horario generado exitosamente!.", "success")
    except Exception as e:
        flash(f"Error generando horario: {str(e)}", "danger")
    return redirect(url_for("schedule.index"))


@schedule_bp.route("/download")
def download():
    try:
        schedule = get_schedule()
        df = pd.DataFrame(schedule.values())

        output = io.BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            df.to_excel(writer, index=False)

        output.seek(0)
        return send_file(
            output,
            download_name="horario.xlsx",
            as_attachment=True,
            mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
    except Exception as e:
        flash(f"Error descargando horario: {str(e)}", "danger")
        return redirect(url_for("schedule.index"))

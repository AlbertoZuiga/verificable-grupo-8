import io

import pandas as pd
from flask import Blueprint, flash, redirect, render_template, send_file, url_for

from app.services.generate_schedule import (
    delete_assigned_time_blocks,
    generate_schedule,
    get_schedule,
)

schedule_bp = Blueprint("schedule", __name__, url_prefix="/schedule")


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
    except RuntimeError as e:
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
    except (IOError, ValueError, KeyError, TypeError) as e:
        flash(f"Error descargando horario: {str(e)}", "danger")
        return redirect(url_for("schedule.index"))

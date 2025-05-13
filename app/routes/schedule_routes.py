from flask import Blueprint, render_template, request, redirect, url_for, flash
from app import kanvas_db
from app.models import AssignedTimeBlock, TimeBlock
from app.services import generate_schedule, delete_assigned_time_blocks

schedule_bp = Blueprint('schedule', __name__, url_prefix='/schedule')

@schedule_bp.route('/')
def index():
    clean_schedule = {}
    schedule = (
        kanvas_db.session.query(AssignedTimeBlock)
        .join(TimeBlock, TimeBlock.id == AssignedTimeBlock.time_block_id)
        .order_by(TimeBlock.start_time)
        .all()
    )
    
    for entry in schedule:
        if entry.section_id not in clean_schedule:
            clean_schedule[entry.section_id] = {
                'course_title': entry.section.course_instance.course.title,
                'course_code': entry.section.course_instance.course.code,
                'section_code': entry.section.code,
                'classroom': entry.classroom.name,
                'weekday': entry.time_block.weekday,
                'start_time': entry.time_block.start_time.strftime('%H:%M'),
                'stop_time': entry.time_block.stop_time.strftime('%H:%M')
            }
        else:
            clean_schedule[entry.section_id]['stop_time'] = entry.time_block.stop_time.strftime('%H:%M')
        print(f"Section {entry.section_id} to {clean_schedule[entry.section_id]['stop_time']}")

    return render_template('schedule/index.html', schedule=clean_schedule)

@schedule_bp.route('/generate')
def generate():
    try:
        delete_assigned_time_blocks()
        generate_schedule()
        flash('Horario generado exitosamente!.', 'success')
    except Exception as e:
        flash(f'Error generando horario: {str(e)}', 'danger')
    return redirect(url_for('schedule.index'))

@schedule_bp.route('/download')
def download():
    try:
        flash('Horario descargado exitosamente!.', 'success')
    except Exception as e:
        flash(f'Error descargando horario: {str(e)}', 'danger')
    return redirect(url_for('schedule.index'))
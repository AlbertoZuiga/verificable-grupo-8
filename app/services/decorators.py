from functools import wraps

from flask import flash, redirect, request, url_for


def handle_closed_section(section):
    flash("Esta sección está cerrada y no puede ser modificada.", "warning")
    return redirect(url_for("section.show", id=section.id))


def require_section_open(get_section_func):
    def decorator(view_func):
        @wraps(view_func)
        def wrapped_view(*args, **kwargs):
            section = get_section_func(**kwargs)
            if section.closed:
                return handle_closed_section(section)
            return view_func(*args, **kwargs)

        return wrapped_view

    return decorator

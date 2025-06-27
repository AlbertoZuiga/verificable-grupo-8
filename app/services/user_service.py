from app import kanvas_db
from app.models import User


def create_user_from_form(form):
    new_user = User(
        first_name=form.first_name.data,
        last_name=form.last_name.data,
        email=form.email.data,
    )
    new_user.set_password(form.password.data)
    kanvas_db.session.add(new_user)
    kanvas_db.session.flush()
    return new_user

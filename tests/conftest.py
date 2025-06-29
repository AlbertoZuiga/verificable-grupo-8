# pylint: disable=redefined-outer-name
import uuid

import pytest

from app import create_app
from app.extensions import kanvas_db
from app.models.user import User


@pytest.fixture(scope='session')
def app():
    test_app = create_app(testing=True)
    test_app.config.update({
        'SERVER_NAME': 'localhost',
        'APPLICATION_ROOT': '/',
        'PREFERRED_URL_SCHEME': 'http'
    })
    with test_app.app_context():
        yield test_app

@pytest.fixture
def db(app):
    with app.app_context():
        kanvas_db.create_all()
        yield kanvas_db
        kanvas_db.session.remove()
        kanvas_db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def runner(app):
    return app.test_cli_runner()


@pytest.fixture
def test_user(db):
    email = f"test_{uuid.uuid4().hex}@example.com"
    user = User(
        email=email,
        first_name="Test",
        last_name="User"
    )
    user.set_password("testpassword")
    db.session.add(user)
    db.session.commit()
    return user

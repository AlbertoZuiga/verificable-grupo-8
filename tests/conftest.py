# pylint: disable=redefined-outer-name
import pytest

from app import create_app
from app.extensions import kanvas_db


@pytest.fixture(scope='module')
def app():
    test_app = create_app(testing=True)
    # Configure URL generation settings
    test_app.config.update({
        'SERVER_NAME': 'localhost',
        'APPLICATION_ROOT': '/',
        'PREFERRED_URL_SCHEME': 'http'
    })

    # Push application context for the entire test module
    ctx = test_app.app_context()
    ctx.push()

    # Create database schema
    kanvas_db.create_all()

    yield test_app

    # Clean up after tests
    kanvas_db.drop_all()
    ctx.pop()

@pytest.fixture
def db(app):
    yield kanvas_db

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def runner(app):
    return app.test_cli_runner()
from app import kanvas_app
from app.db.create import create_database
from app.db.migrate import migrate_database


def setup():
    with kanvas_app.app_context():
        create_database()
        migrate_database()


if __name__ == "__main__":
    setup()

from app import kanvas_app
from app.extensions import kanvas_db

with kanvas_app.app_context():
    kanvas_db.create_all()

if __name__ == "__main__":
    kanvas_app.run()

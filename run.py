from app import app, kanvas_db

with app.app_context():
    kanvas_db.create_all()

if __name__ == '__main__':
    app.run()
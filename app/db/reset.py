from app import app, kanvas_db

def reset_database():
    with app.app_context():
        kanvas_db.drop_all()
        kanvas_db.create_all()
        print("Base de datos reseteada con éxito.\n")

if __name__ == "__main__":
    reset_database()

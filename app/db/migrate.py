from app import app, kanvas_db

def migrate_database():
    with app.app_context():
        print("Migrando base de datos...")
        kanvas_db.create_all()
        print("Base de datos migrada con éxito.\n")

if __name__ == "__main__":
    migrate_database()

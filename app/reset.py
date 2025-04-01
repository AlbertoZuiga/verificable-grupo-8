from app import create_app, db  # Importa la instancia de SQLAlchemy

def reset_db():
    """Elimina todas las tablas y las vuelve a crear."""
    
    app = create_app()  # Inicializa la aplicación Flask correctamente
    with app.app_context():
        db.drop_all()  # Elimina todas las tablas
        db.create_all()  # Vuelve a crear todas las tablas
        print("Base de datos reseteada con éxito.")

if __name__ == "__main__":
    reset_db()

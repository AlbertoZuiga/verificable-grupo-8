from flask import Flask
from config import Config
from models import db
from routes import init_app

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    init_app(app)

    with app.app_context():
        db.create_all()

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)

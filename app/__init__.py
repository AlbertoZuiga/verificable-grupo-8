from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import Config

kanvas_db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    kanvas_db.init_app(app)

    from app.routes import blueprints
    for bp in blueprints:
        app.register_blueprint(bp)

    return app

app = create_app()
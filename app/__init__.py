from flask import Flask
from flask_login import LoginManager

from app.extensions import kanvas_db
from app.models.user import User
from app.routes import blueprints
from config import Config

login_manager = LoginManager()


def create_app(testing=False):
    app = Flask(__name__)
    if testing:
        app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
        app.config["TESTING"] = True
        app.config["WTF_CSRF_ENABLED"] = False
        app.config["SECRET_KEY"] = "test-secret-key"
    else:
        app.config.from_object(Config)
    kanvas_db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    for bp in blueprints:
        app.register_blueprint(bp)

    return app


kanvas_app = create_app()

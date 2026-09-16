from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from flask_migrate import Migrate

db = SQLAlchemy()
csrf = CSRFProtect()
migrate = Migrate()


def create_app():
    app = Flask(__name__)
    app.config.from_object("config.Config")

    db.init_app(app)
    csrf.init_app(app)
    migrate.init_app(app, db)

    # Importa os models para que o Alembic consiga detectá-los
    from app import models

    from app.routes import main_bp
    app.register_blueprint(main_bp)

    return app
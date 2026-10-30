from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from flask_migrate import Migrate
from flask_login import LoginManager


db = SQLAlchemy()
csrf = CSRFProtect()
migrate = Migrate()
login_manager = LoginManager()

login_manager.login_view = "auth.login"
login_manager.login_message = "Faça login para acessar esta página."
login_manager.login_message_category = "info"


def create_app():
    app = Flask(__name__)
    app.config.from_object("config.Config")

    db.init_app(app)
    csrf.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    from app import models
    from app.models import Usuario

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(Usuario, int(user_id))

    from app.routes import main_bp
    from app.routes.pessoas import pessoas_bp
    from app.routes.acompanhamentos import acompanhamentos_bp
    from app.routes.auth import auth_bp
    from app.routes.tarefas import tarefas_bp
    from app.routes.usuarios import usuarios_bp
    from app.routes.pequenos_grupos import pequenos_grupos_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(pessoas_bp)
    app.register_blueprint(acompanhamentos_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(tarefas_bp)
    app.register_blueprint(usuarios_bp)
    app.register_blueprint(pequenos_grupos_bp)

    @app.errorhandler(403)
    def forbidden(error):
        return render_template("errors/403.html"), 403

    return app
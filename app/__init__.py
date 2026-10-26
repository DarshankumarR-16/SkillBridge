
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect

from config import Config

db = SQLAlchemy()
migrate = Migrate()
csrf = CSRFProtect()


def create_app(config_class=Config):
    flask_app = Flask(__name__)
    flask_app.config.from_object(config_class)

    # Enable CSRF protection for POST and other state-changing requests.
    csrf.init_app(flask_app)

    # Initialize database and migrations.
    db.init_app(flask_app)
    migrate.init_app(flask_app, db)

    # Load models so Flask-Migrate can detect their tables.
    import app.models  # noqa: F401

    # Register application routes.
    from app.routes import auth
    flask_app.register_blueprint(auth)

    @flask_app.get("/")
    def index():
        from app.models import Skill, Project

        skills = Skill.query.order_by(Skill.name.asc()).all()
        projects = Project.query.filter_by(is_active=True).order_by(
            Project.title.asc()
        ).all()

        return render_template(
            "index.html",
            skills=skills,
            projects=projects,
        )

    @flask_app.get("/health")
    def health():
        return {"status": "ok", "application": "SkillBridge"}

    @flask_app.errorhandler(404)
    def page_not_found(error):
        return render_template("404.html"), 404

    return flask_app

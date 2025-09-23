import os
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_dance.contrib.google import make_google_blueprint, google
from datetime import datetime
from .config import Config

os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'  # local HTTP

db = SQLAlchemy()
migrate = Migrate()

google_bp = make_google_blueprint(
    client_id=os.getenv("GOOGLE_CLIENT_ID"),
    client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
    scope=[
        "openid",
        "https://www.googleapis.com/auth/userinfo.profile",
        "https://www.googleapis.com/auth/userinfo.email"
    ],
    redirect_url="/dashboard"
)

def create_app():
    app = Flask(__name__ , static_folder="static", static_url_path="/static")
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)
    app.register_blueprint(google_bp, url_prefix="/login")

    # Context processor
    @app.context_processor
    def inject_globals():
        return {
            "google": google,
            "current_year": datetime.now().year
        }

    # Register blueprints
    from .routes import main_bp
    app.register_blueprint(main_bp)

    from .auth import auth_bp
    app.register_blueprint(auth_bp)

    # Error handler
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template("404.html"), 404

    return app

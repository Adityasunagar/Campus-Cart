from flask import Flask
from pathlib import Path
from config.settings import SECRET_KEY
from app.routes import register_blueprints
from app.extensions import socketio
from utils.db import init_db, close_db


def create_app():
    # Get the root directory (parent of app/)
    root_dir = Path(__file__).resolve().parent.parent
    
    app = Flask(
        __name__,
        template_folder=str(root_dir / 'template'),
        static_folder=str(root_dir / 'static'),
    )
    app.config.from_mapping(SECRET_KEY=SECRET_KEY)

    register_blueprints(app)
    app.teardown_appcontext(close_db)

    socketio.init_app(app, cors_allowed_origins='*', manage_session=False)

    with app.app_context():
        init_db()

    return app


__all__ = ['create_app', 'socketio']

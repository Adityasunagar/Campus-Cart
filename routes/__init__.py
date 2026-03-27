from .auth import auth_bp
from .items import main_bp
from .chat import chat_bp
from .admin import admin_bp
from .profile import profile_bp

def register_blueprints(app):
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(chat_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(profile_bp)

    @app.context_processor
    def inject_current_user():
        from flask import session
        from models.user import User

        current_user = None
        if session.get('user_id'):
            current_user = User.find_by_id(session['user_id'])
        return {"current_user": current_user}

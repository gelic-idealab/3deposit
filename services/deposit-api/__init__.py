from flask import Flask
from flask_login import LoginManager
from logging.config import dictConfig
from threedeposit.admin.bp import admin
from threedeposit.user.bp import user
from threedeposit.public.bp import public


def create_app():
    """
    Flask application factory
    Declares configs, database connection, login manager, logging
    Registers routes from blueprints
    """
    app = Flask(__name__)
    app.config['SECRET_KEY'] = '5791628bb0b13de0c676dfce280ba245'

    from threedeposit.database import db_session, User

    @app.teardown_appcontext
    def shutdown_session(exception=None):
        db_session.remove()

    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'admin.login'
    login_manager.login_message = 'Please log in.'
    login_manager.login_message_category = 'info'

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.filter_by(id=user_id).first()

    # Logging
    log_path = 'app.log'
    dictConfig({
        'version': 1,
        'formatters': {'default': {
            'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
        }},
        'handlers': {'wsgi': {
            'class': 'logging.StreamHandler',
            'stream': 'ext://flask.logging.wsgi_errors_stream',
            'formatter': 'default'
        },
            'file': {
                'class': 'logging.handlers.RotatingFileHandler',
                'filename': log_path,
                'formatter': 'default'
        }},
        'root': {
            'level': 'INFO',
            'handlers': ['wsgi', 'file']
        }
    })

    # Routes

    app.register_blueprint(admin, url_prefix='/admin')
    app.register_blueprint(user, url_prefix='/user')
    app.register_blueprint(public)

    return app

from flask import Flask
from flask_pymongo import PyMongo
from redis import Redis
from celery import Celery
from flask_login import LoginManager
from config.settings import Config
from app.errors import register_error_handlers
from app.services.celery_setup import make_celery, init_background_tasks

# Initialize extensions
mongo = PyMongo()
redis_client = Redis()
celery = Celery()
login_manager = LoginManager()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions with app
    mongo.init_app(app)
    redis_client.from_url(app.config['REDIS_URL'])
    celery = make_celery(app)
    login_manager.init_app(app)

    # Register blueprints
    from app.auth.routes import auth_bp
    from app.api.routes import api_bp
    from app.routes.main import main_bp
    
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(main_bp)

    # Register error handlers
    register_error_handlers(app)

    # Initialize background tasks
    init_background_tasks(app)

    return app
"""Main Flask app for the website and api."""
from flask import Flask
from flask_app.extensions import bootstrap, csrf
import flask_app.views as views
import logging

CONFIG = {
    "environment": "testing"
}


def setup_config():
    """Helper function to configure environment based on config."""
    if CONFIG.get("environment", "server") == 'production':
        return 'config.ProductionConfig'
    else:
        return 'config.TestingConfig'


def create_app():
    """Main application factory."""
    app = Flask(__name__)

    # Use helper function to source environment from config
    environment = setup_config()
    app.config.from_object(environment)

    # Setup logging level
    if environment == 'config.ProductionConfig':
        logging.basicConfig(level=logging.WARN)
    else:
        logging.basicConfig(level=logging.DEBUG)

    register_extensions(app)
    register_blueprints(app)

    return app


def register_extensions(app):
    """Register flask extensions."""
    bootstrap.init_app(app)
    csrf.init_app(app)


def register_blueprints(app):
    """Register flask blueprints."""
    app.register_blueprint(views.home_blueprint)
    app.register_blueprint(views.api_blueprint, url_prefix='/api/v1/')


def register_errors(app):
    """Register flask error handling."""
    # TODO
    pass

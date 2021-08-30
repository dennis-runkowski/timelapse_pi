"""Contains all the config for the app."""

import os


class BaseConfig:
    """Base Config for our application."""

    # TODO Change
    SECRET_KEY = '1234'


class ProductionConfig(BaseConfig):
    """Production config for the application."""

    ENV = 'production'
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    DEBUG = False
    # SERVER_NAME = '0.0.0.0'
    SQLALCHEMY_DATABASE_URI = ''
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 465
    MAIL_USE_SSL = True
    MAIL_USERNAME = ''
    MAIL_PASSWORD = ''
    MAIL_DEBUG = False
    MAIL_SUPPRESS_SEND = False


class TestingConfig(BaseConfig):
    """Testing config for the application."""

    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    ENV = 'THIS APP IS IN DEBUG MODE. YOU SHOULD NOT SEE THIS IN PRODUCTION.'
    DEBUG = True
    TESTING = True
    # SERVER_NAME = '0.0.0.0'
    # SQLALCHEMY_DATABASE_URI = 'sqlite:///main.db'
    SQLALCHEMY_DATABASE_URI = ''
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 465
    MAIL_USE_SSL = True
    MAIL_USERNAME = ''
    MAIL_PASSWORD = ''
    MAIL_DEBUG = True
    MAIL_SUPPRESS_SEND = False

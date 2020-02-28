""" Carafe Configration """
import os
from os import environ


def load_config(app):
    """
    loads application configuration variables
    """

    app.config['DEBUG'] = os.getenv(
        'FLASK_ENV', 'development') == 'development'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['NAME'] = os.getenv('CARAFE_APPLICATION_NAME', 'Carafe')
    if app.config['DEBUG']:
        app.config['SECRET_KEY'] = 'Not so secret key'
        app.config['SQLALCHEMY_DATABASE_URI'] = (
            'postgresql://postgres:password@localhost/postgres'
        )
        app.config['THREADED'] = False
    else:
        app.config['THREADED'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = environ['DATABASE_URL']
        app.config['SECRET_KEY'] = environ['SECRET_KEY']

    app.config['PORT'] = os.getenv('CARAFE_PORT', 8000)
    app.config['REGISTRATION_FLAG'] = os.getenv(
        'CARAFE_REGISTRATION') == 'true'
    app.config['HOST'] = os.getenv('CARAFE_HOST', '0.0.0.0')

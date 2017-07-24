from os import environ


def load_config(app):
    app.config['DEBUG'] = True
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['NAME'] = 'Carafe'
    app.config['LOCAL'] = False
    if app.config['LOCAL']:
        app.config['SECRET_KEY'] = 'Not so secret key'
        app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:password@localhost/postgres'
    else:
        app.config['SQLALCHEMY_DATABASE_URI'] = environ['DATABASE_URL']
        app.config['SECRET_KEY'] = environ['SECRET_KEY']

    app.config['PORT'] = 8000
    app.config['SETUP'] = False
    app.config['REGISTRATION_FLAG'] = True

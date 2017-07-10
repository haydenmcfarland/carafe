from os import environ


class Config:
    SECURITY_PASSWORD_SALT = 'SALTY SALT [REPLACE THIS]'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DEBUG = True
    SECRET_KEY = 'SUPER SECRET KEY [REPLACE THIS]'
    NAME = 'Carafe'


class Local(Config):
    SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:password@localhost/postgres'


class Production(Config):
    SQLALCHEMY_DATABASE_URI = environ['DATABASE_URL']
    PORT = 8000
    DEBUG = False

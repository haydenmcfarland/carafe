from os import environ

PARAMETERS_TO_LOAD = ['LOCAL', 'SETUP', 'PORT', 'SQLALCHEMY_DATABASE_URI', 'NAME', 'REGISTRATION_FLAG',
                      'SECRET_KEY', 'DEBUG', 'SQLALCHEMY_TRACK_MODIFICATIONS']


def load_config(app):
    with open('config.conf') as conf:
        for c in conf.readlines():
            pair = tuple(i.strip() for i in c.split('='))
            if pair[-1] in ['False', 'True']:
                app.config[pair[0]] = (pair[-1] == 'True')
            elif pair[0] == 'SQLALCHEMY_DATABASE_URI' and pair[-1] == 'ENVIRON':
                app.config[pair[0]] = environ['DATABASE_URL']
            else:
                app.config[pair[0]] = pair[-1]


def update_config(app):
    with open('config.conf', 'w') as conf:
        conf.write('\r\n'.join('{} = {}'.format(k, app.config[k]) for k in app.config if k in PARAMETERS_TO_LOAD))

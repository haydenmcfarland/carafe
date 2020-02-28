""" Carafe - Flask Message Board """
from os import environ
from carafe.app import APP

if __name__ == '__main__':
    APP.run(
        host='0.0.0.0',
        port=APP.config['PORT'],
        threaded=APP.config['THREADED'],
        debug=APP.config['DEBUG'])

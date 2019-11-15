""" Carafe - Flask Message Board """
from os import environ
from carafe.app import APP

if __name__ == '__main__':
    if APP.config['LOCAL']:
        APP.run()
    else:
        PORT = int(environ.get('PORT', APP.config['PORT']))
        APP.run(
            host='0.0.0.0',
            port=PORT,
            threaded=APP.config['THREADED'],
            debug=APP.config['DEBUG'])

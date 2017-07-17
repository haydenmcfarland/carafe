from os import environ
from carafe.app import app

if __name__ == '__main__':
    if app.config['LOCAL']:
        app.run()
    else:
        port = int(environ.get('PORT', app.config['PORT']))
        app.run(host='0.0.0.0', port=port, threaded=app.config['THREADED'], debug=app.config['DEBUG'])

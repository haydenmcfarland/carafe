from carafe.app import app as carafeboard

if __name__ == '__main__':
    port = int(environ.get('PORT', carafeboard['PORT']))
    carafeboard.run(host='0.0.0.0', port=port, threaded=True, debug=carafeboard['PORT'])

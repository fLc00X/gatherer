import flask

api_version = '0.1'
api_url_prefix = '/api/gatherer/v1'

app = flask.Flask(__name__)

#@app.route(api_url_prefix + '/', methods = ['GET'])
@app.route('/', methods = ['GET'])
def content():
    return flask.jsonify({'name': 'gatherer API',
                          'version': api_version})
if __name__ == '__main__':
    print 'gatherer API (' + api_version + ')'
    app.run(debug = False)

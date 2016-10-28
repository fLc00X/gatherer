import flask

app_version = '0.1'

app = flask.Flask(__name__)

@app.route('/', methods = ['GET'])
def content():
    return flask.jsonify({'name': 'gatherer',
                          'version': app_version})

@app.route('/gatherer_app', methods = ['GET'])
def text():
    r = flask.make_response('gatherer_app')
    r.mimetype = 'text/plain'
    return r

if __name__ == '__main__':
    print 'gatherer (' + app_version + ')'
    app.run(debug = False)

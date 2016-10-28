import flask

app_version = '0.1'

app = flask.Flask(__name__)

@app.route('/', methods = ['GET'])
def content():
    return flask.jsonify({'name': 'gatherer',
                          'version': app_version})

@app.route('/text', methods = ['GET'])
def text():
    r = flask.make_response('text')
    r.mimetype = 'text/plain'
    return r

@app.route('/gather_stations', methods = ['GET'])
def gather_stations():
    print 'gatherer_stations started'
    host = 'www.gasbuddy.com/Station'
    stations = {'2731': 'Station@Someplace'}
    return flask.jsonify({'stations':
                          [(host, station, name) for station, name in stations.items()]})

if __name__ == '__main__':
    print 'gatherer (' + app_version + ')'
    app.run(debug = False)

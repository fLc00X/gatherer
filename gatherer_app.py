import flask
import json
import time
import urllib
import urllib2

def readUrl(url):
    request = urllib2.Request(url)
    try:
        response = urllib2.urlopen(request)
        return (response.getcode(), response.read())
    except urllib2.HTTPError as httpError:
        return (httpError.getcode(), httpError.read())
    except Exception as error:
        return (-1, "readUrl::error occurred:" + str(error))

def gatherStation(host, station, name):
    print 'station:' + station + ' (' + name + ')'
    print 'http://' + host + '/' + station
    code, data = readUrl('http://' + host + '/' + station)
    if code == 200:
        prices = []
        for line in data.split('\n'):
            if 'price-display credit-price' in line:
                prices.append(line.split('>')[1].split('<')[0])
        data = {'timestamp': time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()),
                'regular':  prices[0] if len(prices) > 0 else -1.00,
                'midgrade': prices[1] if len(prices) > 1 else -1.00,
                'premium':  prices[2] if len(prices) > 2 else -1.00}
        print data
        return data
    else:
        print "error occurred"

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
                          [gatherStation(host, station, name) for station, name in stations.items()]})

if __name__ == '__main__':
    print 'gatherer (' + app_version + ')'
    app.run(debug = False)

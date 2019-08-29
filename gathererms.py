import atexit
import os
import threading

from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
from flask import Flask, jsonify, make_response

from aqi_gatherer import AqiGatherer
from gasoline_gatherer import GasolineGatherer
from rxtxapi import RxtxApi
from weather_gatherer import WeatherGatherer

VERSION = '0.22'
started = datetime.utcnow()
_status = {}

app = Flask(__name__)
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False

@app.route('/api', methods = ['GET'])
def version():
    return jsonify({'name': 'fLc004 @IBM Cloud Foundry',
                    'version': VERSION,
                    'uptime': (datetime.utcnow() - started).total_seconds()})

@app.route('/api/status', methods = ['GET'])
def status():
    return jsonify(_status)

@app.errorhandler(400)
def bad_request(error):
    return make_response(jsonify({'error': 'bad request'}), 400)

@app.errorhandler(401)
def not_authorized(error):
    return make_response(jsonify({'error': 'not authorized'}), 401)

@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'not found'}), 404)

def log(message):
    print '|'.join(['gathererms',
                    datetime.now().strftime('%Y-%m-%dT%H:%M:%S'),
                    message])

def env(name):
    if os.environ.get(name):
        return os.environ[name]
    else:
        raise Exception(name + ' is not set up')

rxtxapi = RxtxApi(env('RXTXAPI_URI'),
                  {'POST': env('RXTXAPI_POST_KEY'),
                   'PUT': env('RXTXAPI_PUT_KEY'),
                   'GET': env('RXTXAPI_GET_KEY'),
                   'DELETE': env('RXTXAPI_DELETE_KEY')})
gasolineGatherer = \
GasolineGatherer(int(env('GATHERER_WORKER_GAS_STATIONS_INTERVAL')),
                 rxtxapi,
                 env('GATHERER_WORKER_GAS_STATIONS_URL'),
                 [s.split(':') for s in \
                  env('GATHERER_WORKER_GAS_STATIONS').split(';')])
weatherGatherer = \
WeatherGatherer(int(env('GATHERER_WORKER_WEATHER_STATIONS_INTERVAL')),
                rxtxapi,
                env('GATHERER_WORKER_WEATHER_STATIONS_URL'),
                [s.split(':') for s in \
                 env('GATHERER_WORKER_WEATHER_STATIONS').split(';')],
                int(env('GATHERER_WORKER_WEATHER_STATIONS_IDLE_INTERVAL')))
aqiGatherer = AqiGatherer(int(env('GATHERER_WORKER_AQI_STATIONS_INTERVAL')),
                          rxtxapi,
                          env('GATHERER_WORKER_AQI_STATIONS_URL'),
                          [s.split(':') for s in \
                           env('GATHERER_WORKER_AQI_STATIONS').split(';')])

def gather():
    for name, gatherer in (('gasoline', gasolineGatherer),
                           ('weather', weatherGatherer),
                           ('aqi', aqiGatherer)):
        log('gathering [' + name + '] ...')
        start = datetime.utcnow()
        data = gatherer.gather()
        if data:
            _status[name] = \
            {'totalRunsCount': \
             _status.get(name, {'totalRunsCount': 0})['totalRunsCount'] + 1,
             'latestStart': datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%f'),
             'latestDuration': (datetime.utcnow() - start).total_seconds()}
            log(name + ':' + str(data))
    log('finished')

scheduler = BackgroundScheduler()
scheduler.add_job(func = gather,
                  trigger = 'interval',
                  seconds = int(env('GATHERER_WORKER_INTERVAL')))
scheduler.start()
atexit.register(lambda: scheduler.shutdown())

log('version ' + VERSION)
log(__name__)
if __name__ == '__main__':
    threading.Thread(target = gather).start()
    app.run(host = '0.0.0.0',
            port = int(os.getenv('PORT', 8000)),
            debug = False)
log('done')

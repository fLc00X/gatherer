#!/bin/python

import os
import threading
import time

from rxtxapi import RxtxApi
from gasoline_gatherer import GasolineGatherer
from weather_gatherer import WeatherGatherer

def log(message):
    print 'gatherer|' + message

def env(name):
    if os.environ.get(name):
        return os.environ[name]
    else:
        raise Exception(name + ' is not set up')

def gather():
    rxtxapi = RxtxApi(env('RXTXAPI_URI'),
                      {'POST': env('RXTXAPI_POST_KEY'),
                       'PUT': env('RXTXAPI_PUT_KEY'),
                       'GET': env('RXTXAPI_GET_KEY'),
                       'DELETE': env('RXTXAPI_DELETE_KEY')})
    gasolineGatherer = GasolineGatherer(int(env('GATHERER_WORKER_GAS_STATIONS_INTERVAL')),
                                        rxtxapi,
                                        env('GATHERER_WORKER_GAS_STATIONS_URL'),
                                        [s.split(':') for s in env('GATHERER_WORKER_GAS_STATIONS').split(';')])
    weatherGatherer = WeatherGatherer(int(env('GATHERER_WORKER_WEATHER_STATIONS_INTERVAL')),
                                      rxtxapi,
                                      env('GATHERER_WORKER_WEATHER_STATIONS_URL'),
                                      [s.split(':') for s in env('GATHERER_WORKER_WEATHER_STATIONS').split(';')],
                                      int(env('GATHERER_WORKER_WEATHER_STATIONS_IDLE_INTERVAL')))
    aqiGatherer = AqiGatherer(int(env('GATHERER_WORKER_AQI_STATIONS_INTERVAL')),
                              rxtxapi,
                              env('GATHERER_WORKER_AQI_STATIONS_URL'),
                              [s.split(':') for s in env('GATHERER_WORKER_AQI_STATIONS').split(';')])
    while True:
        for name, gatherer in (('gasoline', gasolineGatherer),
                               ('weather', weatherGatherer),
                               ('aqi', aqiGatherer)):
            log('gathering [' + name + '] ...')
            data = gatherer.gather()
            if data:
                log(name + ':' + str(data))
        log('finished')
        time.sleep(int(env('GATHERER_WORKER_INTERVAL')))

log('version 0.15')
log(__name__)
if __name__ == '__main__':
    gather()
else:
    threading.Thread(target = gather).start()
log('done')

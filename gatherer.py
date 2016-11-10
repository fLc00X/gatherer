#!/bin/python

import os
import threading
import time

from rxtxapi import RxtxApi
from gasoline_gatherer import GasolineGatherer

def log(message):
    print 'gatherer|' + message

def env(name):
    if os.environ.get(name):
        return os.environ[name]
    else:
        raise Exception(name + ' is not set up')

def worker():
    gasolineGatherer = GasolineGatherer(int(env('GATHERER_WORKER_GAS_STATIONS_INTERVAL')),
                                        RxtxApi(env('RXTXAPI_URI'),
                                                {'POST': env('RXTXAPI_POST_KEY'),
                                                 'PUT': env('RXTXAPI_PUT_KEY'),
                                                 'GET': env('RXTXAPI_GET_KEY'),
                                                 'DELETE': env('RXTXAPI_DELETE_KEY')}),
                                        env('GATHERER_WORKER_GAS_STATIONS_URL'),
                                        [s.split(':') for s in env('GATHERER_WORKER_GAS_STATIONS_STATIONS').split(',')])
    while True:
        log('start gathering ...')
        data = gasolineGatherer.gather()
        if data:
            log('gasoline:' + str(data))
        log('done gathering')
        time.sleep(int(env('GATHERER_WORKER_INTERVAL')))

log('version 0.10')
log(__name__)
if __name__ == '__main__':
    worker()
else:
    t = threading.Thread(target = worker)
    t.start()
log('done')

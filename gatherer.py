#!/bin/python

import os
import threading

import rxtxapi
from gasoline_gatherer import GasolineGatherer

def log(message):
    print 'gatherer|' + message

def getVar(name):
    if os.environ.get(name):
        return os.environ[name]
    else:
        raise Exception(name + ' is not set up')

def worker():
    api = rxtxapi.RxtxApi(getVar('RXTXAPI_URI'),
                          {'POST': getVar('RXTXAPI_POST_KEY'),
                           'PUT': getVar('RXTXAPI_PUT_KEY'),
                           'GET': getVar('RXTXAPI_GET_KEY'),
                           'DELETE': getVar('RXTXAPI_DELETE_KEY')})
    gasolineGatherer = GasolineGatherer(int(getVar('GATHERER_WORKER_GAS_STATIONS_INTERVAL')),
                                        api,
                                        getVar('GATHERER_WORKER_GAS_STATIONS_URL'),
                                        [s.split(':') for s in getVar('GATHERER_WORKER_GAS_STATIONS_STATIONS').split(',')])
    while True:
        data = gasolineGatherer.gather()
        if data:
            log('gasolineGatherer:' + str(data))
        time.sleep(int(getVar('GATHERER_WORKER_INTERVAL')))

log('version 0.9')
log(__name__)
if __name__ == '__main__':
    worker()
else:
    t = threading.Thread(target = worker)
    t.start()
log('done')

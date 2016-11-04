#!/bin/python

import datetime
import os
import time
import threading
import urllib
import urllib2

import rxtxapi

def log(message):
    print 'gatherer_worker|' + message

def readUrl(url):
    request = urllib2.Request(url)
    try:
        response = urllib2.urlopen(request)
        return (response.getcode(), response.read())
    except urllib2.HTTPError as httpError:
        return (httpError.getcode(), httpError.read())
    except Exception as error:
        return (-1, "readUrl::error occurred:" + str(error))

def timestamp():
    return datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%f')

def gatherStation(host, station, name):
    code, data = readUrl('http://' + host + '/' + station)
    if code == 200:
        prices = []
        for line in data.split('\n'):
            if '<div class="price-display' in line:
                if 'credit-price' in line:
                    prices.append(line.split('>')[1].split('<')[0])
                else:
                    prices.append(-1.00)
        return {'station': station,
                'name': name,
                'status': 'ok',
                'timestamp': timestamp(),
                'regular': prices[1] if len(prices) > 0 else -1.00,
                'midgrade': prices[3] if len(prices) > 1 else -1.00,
                'premium':  prices[5] if len(prices) > 2 else -1.00}
    else:
        return {'station': station,
                'name': name,
                'status': 'error',
                'timestamp': timestamp(),
                'regular': -1.00,
                'midgrade': -1.00,
                'premium': -1.00}

def getVar(name):
    v = os.environ.get(name)
    if v:
        return v
    else:
        raise Exception(name + ' is not set up')

def getStations():
    return [tuple(s.split(':')) for s in getVar('GATHERER_WORKER_GAS_STATIONS_STATIONS').split(',')]

def getHost():
    return getVar('GATHERER_WORKER_GAS_STATIONS_HOST')

def getInterval():
    return int(getVar('GATHERER_WORKER_GAS_STATIONS_INTERVAL'))

def getRxtxApi():
    return rxtxapi.RxtxApi(getVar('RXTXAPI_URI'),
                           {'POST': getVar('RXTXAPI_POST_KEY'),
                            'PUT': getVar('RXTXAPI_PUT_KEY'),
                            'GET': getVar('RXTXAPI_GET_KEY'),
                            'DELETE': getVar('RXTXAPI_DELETE_KEY')})

def worker():
    while True:
        api = getRxtxApi()
        for d in [gatherStation(getHost(), station, name) for station, name in getStations()]:
            log('publish:' + str(d))
            api.publish('gas_stations/' + d['station'], d)
        time.sleep(getInterval())

log('version 0.6')
log(__name__)
if __name__ == '__main__':
    worker()
else:
    t = threading.Thread(target = worker)
    t.start()
    #t.join()
log('done')

#!/bin/python

import time
import threading
import urllib
import urllib2

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
    return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())

def gatherStation(host, station, name):
    code, data = readUrl('http://' + host + '/' + station)
    if code == 200:
        prices = []
        for line in data.split('\n'):
            if 'price-display credit-price' in line:
                prices.append(line.split('>')[1].split('<')[0])
        return {'station': station,
                'name': name,
                'status': 'ok',
                'timestamp': timestamp(),
                'regular': prices[0] if len(prices) > 0 else -1.00,
                'midgrade': prices[1] if len(prices) > 1 else -1.00,
                'premium':  prices[2] if len(prices) > 2 else -1.00}
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
        rise Exception(v + ' is not set up')

def getStations():
    return [tuple(s.split(':')) for s in getVar('GATHERER_WORKER_GAS_STATIONS_STATIONS').split(',')]

def getHost():
    return getVar('GATHERER_WORKER_GAS_STATIONS_HOST')

def getInterval():
    return int(getVar('GATHERER_WORKER_GAS_STATIONS_INTERVAL'))

def worker():
    while True:
        log('data:' + str([gatherStation(getHost(), station, name) for station, name in getStations()]))
        time.sleep(getInterval())

log('version 0.1')
log(__name__)
if __name__ == '__main__':
    worker()
else:
    t = threading.Thread(target = worker)
    t.start()
    #t.join()
log('done')

#!/bin/python

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

apiUri = 'TBD'
apiGetKey = 'TBD'
apiPostKey = 'TBD'
apiPutKey = 'TBD'

def post(name, value):
    request = urllib2.Request(apiUri + '/' + name, urllib.urlencode(
              {'api_key': apiPostKey,
               'parameter': name,
               'value': json.dumps(value)}))
    response = urllib2.urlopen(request, timeout = 10)
    #print str(response.read())

def put(name, value):
    code, data = readUrl(apiUri + '/' + name + '?' + \
                         urllib.urlencode({'method': 'PUT',
                                           'api_key': apiPutKey,
                                           'value': json.dumps(value)}))

def publish(name, value):
    code, data = readUrl(apiUri + '/' + name + '?' + \
                         urllib.urlencode({'api_key': apiGetKey}))
    if code == 200:
        put(name, value)
    else:
        post(name, value)

def updateStation(host, station, name):
    # read & publish
    print 'station:' + station + ' (' + name + ')'
    print 'http://' + host + '/' + station
    code, data = readUrl('http://' + host + '/' + station)
    if code == 200:
        prices = []
        for line in data.split('\n'):
            if 'price-display credit-price' in line:
                prices.append(line.split('>')[1].split('<')[0])
        #publish('/gasstations/' + station + '/latest',
        #        {'timestamp': time.strftime('%Y-%m-%d %H:%M:%S',
        #                                    time.localtime()),
        #         'regular':  prices[0] if len(prices) > 0 else -1.00,
        #         'midgrade': prices[1] if len(prices) > 1 else -1.00,
        #         'premium':  prices[2] if len(prices) > 2 else -1.00})
        data = {'timestamp': time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()),
                'regular':  prices[0] if len(prices) > 0 else -1.00,
                'midgrade': prices[1] if len(prices) > 1 else -1.00,
                'premium':  prices[2] if len(prices) > 2 else -1.00}
        print data
    else:
        print "error occurred"

    # verify
    #code, data = readUrl(apiUri + \
    #                     '/gasstations/' + station + '/latest' + \
    #                     '?' + \
    #                     urllib.urlencode({'api_key': apiGetKey}))
    #if code == 200:
    #    data = json.loads(data)
    #print 'code:' + str(code) + ',data:' + str(data)

print 'gatherer_worker started'

def gatherStations():
    stations = {'2731': 'Station@Someplace'}
    host = 'www.gasbuddy.com/Station'
    return [updateStation(host, station, name) for station, name in stations.items()]

if __name__ == '__main__':
    print 'gatherer_worker started from "__main__"'
    while True:
        for station, name in stations.items():
            updateStation(host, station, name)
            time.sleep(3600)

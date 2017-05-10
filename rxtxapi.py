#!/bin/python

import json
import urllib
import urllib2

def readUrl(url, data = None, method = 'GET', timeout = 10):
    request = urllib2.Request(url,
                              data,
                              {'Pragma': 'no-cache',
                               'Cache-Control': 'no-cache'})
    if method in ['GET', 'POST', 'PUT', 'DELETE']:
        request.get_method = lambda: method
    try:
        response = urllib2.urlopen(request, timeout = timeout)
        result = (response.getcode(), response.read())
        response.close()
        return result
    except urllib2.HTTPError as httpError:
        result = (httpError.getcode(), httpError.read())
        httpError.close()
        return result
    except Exception as error:
        return (-1, "readUrl::error occurred:" + str(error))

class RxtxApi():
    def __init__(self, uri, keys, timeout = 10):
        self.uri = uri
        self.keys = keys
        self.timeout = timeout

    def toJSON(self, data):
        return json.dumps(data, separators = (',', ':'))

    def jsonify(self, data, to_json = True):
        return self.toJSON(data) if to_json else data

    def post(self, name, value, to_json = True):
        ## POST via GET
        #code, data = readUrl(self.uri + '/' + name + '?' + \
        #                     urllib.urlencode(
        #                     {'method': 'POST',
        #                      'api_key': self.keys['POST'],
        #                      'name': name,
        #                      'value': self.jsonify(value, to_json)}),
        #                     timeout = self.timeout)
        return readUrl(self.uri + '/' + name,
                       urllib.urlencode(
                       {'api_key': self.keys['POST'],
                        'name': name,
                        'value': self.jsonify(value, to_json)}),
                       'POST',
                       self.timeout)

    def put(self, name, value, to_json = True):
        ## PUT via GET
        #code, data = readUrl(self.uri + '/' + name + '?' + \
        #                     urllib.urlencode(
        #                     {'method': 'PUT',
        #                      'api_key': self.keys['PUT'],
        #                      'value': self.jsonify(value, to_json)})),
        #                     timeout = self.timeout)
        return readUrl(self.uri + '/' + name,
                       urllib.urlencode(
                       {'api_key': self.keys['PUT'],
                        'value': self.jsonify(value, to_json)}),
                       'PUT',
                       self.timeout)

    def get(self, name):
        return readUrl(self.uri + '/' + name + '?' + \
                       urllib.urlencode({'api_key': self.keys['GET']}),
                       timeout = self.timeout)

    def publish(self, name, value, to_json = True):
        code, data = self.put(name, value, to_json)
        if code == 200 and json.loads(data).get('result', '') == 'Error':
            self.post(name, value, to_json)

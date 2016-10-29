#!/bin/python

import json
import urllib
import urllib2

class RxtxApi():
    def __init__(self, uri, keys, timeout = 10):
        self.uri = uri
        self.keys = keys
        self.timeout = timeout

    def readUrl(self, url):
        request = urllib2.Request(url)
        try:
            response = urllib2.urlopen(request, timeout = self.timeout)
            return (response.getcode(), response.read())
        except urllib2.HTTPError as httpError:
            return (httpError.getcode(), httpError.read())
        except Exception as error:
            return (-1, "readUrl::error occurred:" + str(error))

    def toJSON(self, data):
        return json.dumps(data)

    def jsonify(self, data, to_json = True):
        if to_json:
            return self.toJSON(data)
        else:
            return data

    def post(self, parameter, data, to_json = True):
        request = urllib2.Request(self.uri + '/' + parameter,
                                  urllib.urlencode(
                                  {'api_key': self.keys['POST'],
                                   'parameter': parameter,
                                   'value': self.jsonify(data, to_json)}))
        response = urllib2.urlopen(request, timeout = self.timeout)

    def put(self, parameter, data, to_json = True):
        code, data = self.readUrl(self.uri + '/' + parameter + '?' + \
                                  urllib.urlencode(
                                  {'method': 'PUT',
                                   'api_key': self.keys['PUT'],
                                   'value': self.jsonify(data, to_json)}))

    def get(self, parameter):
        return self.readUrl(self.uri + '/' + parameter + '?' + \
                            urllib.urlencode({'api_key': self.keys['GET']}))

    def publish(self, parameter, data, to_json = True):
        code, data = self.get(parameter)
        if code == 200:
            self.put(parameter, data, to_json)
        else:
            self.post(parameter, data, to_json)

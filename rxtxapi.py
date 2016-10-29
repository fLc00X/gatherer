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

    def post(self, name, value, to_json = True):
        code, data = self.readUrl(self.uri + '/' + name + '?' + \
                                  urllib.urlencode(
                                  {'method': 'POST',
                                   'api_key': self.keys['POST'],
                                   'name': name,
                                   'value': self.jsonify(value, to_json)}))

    def put(self, name, value, to_json = True):
        code, data = self.readUrl(self.uri + '/' + name + '?' + \
                                  urllib.urlencode(
                                  {'method': 'PUT',
                                   'api_key': self.keys['PUT'],
                                   'value': self.jsonify(value, to_json)}))

    def get(self, name):
        return self.readUrl(self.uri + '/' + name + '?' + \
                            urllib.urlencode({'api_key': self.keys['GET']}))

    def publish(self, name, value, to_json = True):
        code, data = self.get(name)
        if code == 200:
            self.put(name, value, to_json)
        else:
            self.post(name, value, to_json)

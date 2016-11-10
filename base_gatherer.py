#!/bin/python

import datetime
import urllib2

class BaseGatherer(object):
    def __init__(self, interval, rxtxapi):
        self.interval = datetime.timedelta(0, interval, 0)
        self.last_run = None;
        self.rxtxapi = rxtxapi

    def collect(self):
        raise NotImplementedError

    def publish(self):
        raise NotImplementedError

    def gather(self):
        now = datetime.datetime.now()
        if self.last_run and (now - self.last_run) < self.interval:
            return
        self.last_run = now
        return self.publish(self.collect())

    def readUrl(self, url):
        request = urllib2.Request(url)
        try:
            response = urllib2.urlopen(request)
            return (response.getcode(), response.read())
        except urllib2.HTTPError as httpError:
            return (httpError.getcode(), httpError.read())
        except Exception as error:
            return (-1, "BaseGatherer.readUrl::error occurred:" + str(error))

    def timestamp(self):
        return datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%f')

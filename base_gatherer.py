#!/bin/python

import datetime

class BaseGatherer(object):
    def __init__(self, interval = 60, rxtxapi):
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
        self.collect()
        self.publish()

def timestamp(self):
    return datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%f')

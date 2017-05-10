#!/bin/python

import datetime

class BaseGatherer(object):
    def __init__(self, interval, rxtxapi):
        self.interval = datetime.timedelta(0, interval, 0)
        self.last_run = None;
        self.rxtxapi = rxtxapi
        self.dtformat = '%Y-%m-%dT%H:%M:%S.%f'

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

    def timestamp(self):
        return datetime.datetime.now().strftime(self.dtformat)

    def fromtimestamp(self, timestamp):
        return datetime.datetime.strptime(timestamp, self.dtformat)

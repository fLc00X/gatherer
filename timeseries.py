#!/bin/python

import datetime
import time

def dt2seconds(dt):
    return int(time.mktime(dt.timetuple()))

def roundSeconds(seconds, granularity):
    return seconds / granularity * granularity

def roundDT(dt, granularity):
    return datetime.datetime.fromtimestamp(roundSeconds(dt2seconds(dt),
                                                        granularity))

class TimeSeries(object):
    def __init__(self, interval, granularity):
        # interval in seconds (ex: 3600 for an interval of one hour)
        self._interval = interval
        # granularity in seconds (ex: 60 for a granularity of one minute)
        self._granularity = granularity
        self._data = {}

    def __setitem__(self, dt, record):
        self._data[roundDT(dt, self._granularity)] = record
        self._trim()

    def __getitem__(self, dt):
        return self._data.get(roundDT(dt, self._granularity))

    def records(self):
        return [(dt, self._data.get(dt)) \
                for dt in self._range(max(self._data.keys()))] \
               if self._data else []

    def _trim(self):
        t = datetime.datetime.fromtimestamp(
            dt2seconds(max(self._data.keys())) - self._interval)
        self._data = {k: v for k, v in self._data.items() if k > t}

    def _range(self, dt):
        seconds = roundSeconds(dt2seconds(dt), self._granularity)
        return [datetime.datetime.fromtimestamp(seconds + s) \
                for s in range(-self._interval + self._granularity,
                               self._granularity,
                               self._granularity)]

    def __str__(self):
        return 'interval:' + str(self._interval) + \
               ', granularity:' + str(self._granularity) + \
               ', data:' + str(self._data)

class Aggregator(object):
    def __init__(self, granularity, parameter):
        # granularity in seconds (ex: 60 for a granularity of one minute)
        self._granularity = granularity
        # parameter is a key for the value in the record's dictionary
        # (ex: 'temperature')
        self._parameter = parameter
        self._callbacks = []
        self._lastDT = None;

    def set(self, dt, record):
        dt = roundDT(dt, self._granularity)
        r = self._process(dt, record)
        for callback in self._callbacks:
            callback(dt, r)

    def _process(self, dt, record):
        raise NotImplementedError

    def addCallback(self, callback):
        self._callbacks.append(callback)

class AvgAggregator(Aggregator):
    def __init__(self, granularity, parameter):
        Aggregator.__init__(self, granularity, parameter)
        self._sum = 0
        self._count = 0

    def _process(self, dt, record):
        if self._lastDT != dt:
            self._lastDT = dt
            self._sum = 0
            self._count = 0
        v = record.get(self._parameter, None)
        if v is not None:
            self._sum += v
            self._count += 1
        return float(self._sum) / self._count if self._count > 0 else None

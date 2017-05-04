#!/bin/python

import datetime
import time

class TimeSeries(object):
    def __init__(self, interval, granularity):
        # interval in seconds (ex: 3600 for an interval of one hour)
        self._interval = interval
        # granularity in seconds (ex: 60 for a granularity of one minute)
        self._granularity = granularity
        self._data = {}

    def __setitem__(self, dt, record):
        self._data[self._roundDT(dt)] = record
        self._trim()

    def __getitem__(self, dt):
        return self._data.get(self._roundDT(dt))

    def records(self):
        return [(dt, self._data.get(dt)) \
                for dt in self._range(max(self._data.keys()))] if self._data else []

    def _trim(self):
        t = datetime.datetime.fromtimestamp(
            self._dt2seconds(max(self._data.keys())) - self._interval)
        self._data = {k: v for k, v in self._data.items() if k > t}

    def _dt2seconds(self, dt):
        return int(time.mktime(dt.timetuple()))

    def _roundSeconds(self, seconds):
        return seconds / self._granularity * self._granularity

    def _roundDT(self, dt):
        seconds = self._roundSeconds(self._dt2seconds(dt))
        return datetime.datetime.fromtimestamp(seconds)

    def _range(self, dt):
        seconds = self._roundSeconds(self._dt2seconds(dt))
        return [datetime.datetime.fromtimestamp(seconds + s) \
                for s in range(-self._interval + self._granularity,
                               self._granularity,
                               self._granularity)]

    def __str__(self):
        return 'interval:' + str(self._interval) + \
               ', granularity:' + str(self._granularity) + \
               ', data:' + str(self._data)

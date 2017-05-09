#!/bin/python

import email.utils
import json
import time
import xml.etree.ElementTree as ElementTree

import base_gatherer
import timeseries

class WeatherGatherer(base_gatherer.BaseGatherer):
    def __init__(self, interval, rxtxapi, url, stations, idleInterval):
        base_gatherer.BaseGatherer.__init__(self, interval, rxtxapi)
        self.url = url
        self.stations = stations
        self.idleInterval = idleInterval
        self.parameters = {'temperature':     'temp_c',
                           'pressure':        'pressure_mb',
                           'humidity':        'relative_humidity',
                           'wind_speed':      'wind_mph',
                           'solar_radiation': 'solar_radiation'}
        self.series = {}
        self.aggregators = {}
        for s, n in self.stations:
            self.series[s + '_minute'] = timeseries.TimeSeries(3600, 60)
            for p in self.parameters:
                ts = timeseries.TimeSeries(24 * 3600, 3600)
                a = timeseries.AvgAggregator(3600, p)
                a.addCallback(ts.__setitem__)
                self.series[s + '_hour_avg_' + p] = ts
                self.aggregators[s + '_avg_' + p] = a
        self.firstRun = True

    def readStation(self, station, name):
        result = {'station': station,
                  'name': name,
                  'status': 'error',
                  'timestamp': self.timestamp()}
        for p in self.parameters:
            result[p] = None
        code, data = self.readUrl(self.url + '?ID=' + station)
        if code == 200:
            root = ElementTree.fromstring(data)
            if self._recent(root):
                for p in self.parameters:
                    s = root.find(self.parameters[p]).text
                    result[p] = float(s) if s else None
                result['status'] = 'ok'
        return result

    def _recent(self, root):
        t = root.findtext('observation_time_rfc822')
        return ((time.mktime(time.localtime()) -
                 email.utils.mktime_tz(email.utils.parsedate_tz(t))) <
                self.idleInterval) if t else False

    def _processSeries(self, series):
        result = {'timestamp': []}
        for t, r in series.records():
            result['timestamp'].append(t.strftime(self.dtformat))
            for p in self.parameters:
                result.setdefault(p, list()).append(r[p] if r else None)
        return result

    def _combineSeries(self, series):
        result = {}
        for p, s in series:
            result['timestamp'] = []
            for t, r in s.records():
                result['timestamp'].append(t.strftime(self.dtformat))
                result.setdefault(p, list()).append(r)
        return result

    def _restore(self):
        for s, n in self.stations:
            code, data = self.rxtxapi.get('weather_stations/' + s + '/hour/avg')
            if code == 200:
                data = json.loads(data)
                for i, t in enumerate(data['timestamp'], 0):
                    dt = self.fromtimestamp(t)
                    for p in self.parameters:
                        self.series[s + '_hour_avg_' + p][dt] = data[p][i]

    def collect(self):
        if self.firstRun:
            self._restore()
        data = []
        for s, r in [(s, self.readStation(s, n)) for s, n in self.stations]:
            if r['status'] == 'ok':
                dt = self.fromtimestamp(r['timestamp'])
                self.series[s + '_minute'][dt] = r
                for p in self.parameters:
                    self.aggregators[s + '_avg_' + p].set(dt, r)
                data.append((s, r))
                data.append((s + '/minute',
                             self._processSeries(self.series[s + '_minute'])))
                data.append((s + '/hour/avg',
                             self._combineSeries(
                             [(p, self.series[s + '_hour_avg_' + p])
                              for p in self.parameters])))
        self.firstRun = False
        return data

    def publish(self, data):
        for parameter, record in data:
            self.rxtxapi.publish('weather_stations/' + parameter, record)
        return data

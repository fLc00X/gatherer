#!/bin/python

import email.utils
import time
import xml.etree.ElementTree as ElementTree

import base_gatherer
import timeseries

class WeatherGatherer(base_gatherer.BaseGatherer):
    def __init__(self, interval, rxtxapi, url, stations):
        base_gatherer.BaseGatherer.__init__(self, interval, rxtxapi)
        self.url = url
        self.stations = stations
        self.parameters = {'temperature':     'temp_c',
                           'pressure':        'pressure_mb',
                           'humidity':        'relative_humidity',
                           'wind_speed':      'wind_mph',
                           'solar_radiation': 'solar_radiation'}
        self.series = {}
        self.aggregators = {}
        for station, name in self.stations:
            self.series[station] = {}
            self.series[station]['minute'] = timeseries.TimeSeries(3600, 60)
            self.series[station]['hour'] = {'avg': {}}
            self.aggregators[station] = {'avg': {}}
            for parameter in self.parameters:
                s = timeseries.TimeSeries(24 * 3600, 3600)
                a = timeseries.AvgAggregator(3600, parameter)
                a.addCallback(s.__setitem__)
                self.aggregators[station]['avg'][parameter] = a
                self.series[station]['hour']['avg'][parameter] = s

    def readStation(self, station, name):
        result = {'station': station,
                  'name': name,
                  'status': 'error',
                  'timestamp': self.timestamp()}
        for parameter in self.parameters:
            result[parameter] = None
        code, data = self.readUrl(self.url + '?ID=' + station)
        if code == 200:
            root = ElementTree.fromstring(data)
            if self._recent(root):
                for parameter in self.parameters:
                    s = root.find(self.parameters[parameter]).text
                    result[parameter] = float(s) if s else None
                result['status'] = 'ok'
        return result

    def _recent(self, root):
        t = root.findtext('observation_time_rfc822')
        return ((time.mktime(time.localtime()) -
                 email.utils.mktime_tz(email.utils.parsedate_tz(t))) < 1800) if t else False

    def _processSeries(self, series, record):
        if record['status'] == 'ok':
            series[self.fromtimestamp(record['timestamp'])] = record
        result = {}
        for t, r in series.records():
            result.setdefault('timestamp', list()).append(t.strftime(self.dtformat))
            for k in self.parameters:
                result.setdefault(k, list()).append(r[k] if r else None)
        return result

    def _combineSeries(self, series):
        result = {}
        for k in series:
            timestamps = []
            for t, r in series[k].records():
                timestamps.append(t.strftime(self.dtformat))
                result.setdefault(k, list()).append(r)
            result['timestamp'] = timestamps
        return result

    def collect(self):
        data = []
        for s, r in [(s, self.readStation(s, n)) for s, n in self.stations]:
            if r['status'] == 'ok':
                data.append((s, r))
                data.append((s + '/minute', self._processSeries(self.series[s]['minute'], r)))
                for a in self.aggregators[s]['avg'].values():
                    a.set(self.fromtimestamp(r['timestamp']), r)
                data.append((s + '/hour/avg', self._combineSeries(self.series[s]['hour']['avg'])))
        return data

    def publish(self, data):
        for parameter, record in data:
            self.rxtxapi.publish('weather_stations/' + parameter, record)
        return data

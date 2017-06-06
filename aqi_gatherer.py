#!/bin/python

import base_gatherer
import timeseries
from rxtxapi import readUrl

class AqiGatherer(base_gatherer.BaseGatherer):
    def __init__(self, interval, rxtxapi, url, stations):
        super(AqiGatherer, self).__init__(interval, rxtxapi)
        self.url = url
        self.stations = stations
        self.parameters = ['ozone', 'pollution']
        self.series = {}
        self.aggregators = {}
        for s, n in self.stations:
            for p in self.parameters:
                ts = timeseries.TimeSeries(24 * 3600, 3600)
                a = timeseries.MaxAggregator(3600, p)
                a.addCallback(ts.__setitem__)
                self.series[s + '_' + p] = ts
                self.aggregators[s + '_' + p] = a
        self.firstRun = True

    def readStation(self, station, name):
        result = {'station': station,
                  'name': name,
                  'status': 'error',
                  'timestamp': self.timestamp()}
        for p in self.parameters:
            result[p] = -1.00
        code, data = readUrl(self.url + '/' + station + '.xml')
        if code == 200:
            prefix = ' - '
            markers = {'ozone': ' AQI - Ozone',
                       'pollution': ' AQI - Particle Pollution (2.5 microns)'}
            for line in data.split('\n'):
                if prefix in line:
                    for key, suffix in markers.items():
                        if suffix in line:
                            result[key] = int(line.split(suffix)[0]
                                                  .split(prefix)[1]
                                                  .strip())
            result['status'] = 'ok'
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
            code, data = self.rxtxapi.get('aqi_stations/' + s + '/hour')
            if code == 200:
                data = json.loads(data)
                for i, t in enumerate(data['timestamp'], 0):
                    dt = self.fromtimestamp(t)
                    for p in self.parameters:
                        self.series[s + '_' + p][dt] = data[p][i] \
                        if p in data else None

    def collect(self):
        if self.firstRun:
            self._restore()
        data = []
        for s, r in [(s, self.readStation(s, n)) for s, n in self.stations]:
            if r['status'] == 'ok':
                dt = self.fromtimestamp(r['timestamp'])
                for p in self.parameters:
                    self.aggregators[s + '_' + p].set(dt, r)
                data.append((s, r))
                data.append((s + '/hour',
                             self._combineSeries(
                             [(p, self.series[s + '_' + p])
                              for p in self.parameters])))
        self.firstRun = False
        return data

    def publish(self, data):
        for parameter, record in data:
            self.rxtxapi.publish('aqi_stations/' + parameter, record)
        return data

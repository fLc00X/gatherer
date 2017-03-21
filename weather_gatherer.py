#!/bin/python

import xml.etree.ElementTree as ElementTree

import base_gatherer

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
        for station in self.stations:
            self.series[station] = {}
            self.series[station]['minute'] = TimeSeries(3600, 60)

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
            for parameter in self.parameters:
                result[parameter] = root.find(self.parameters[parameter]).text
            result['status'] = 'ok'
        return result

    def collect(self):
        data = []
        for s, r in ((s, self.readStation(s, n)) for s, n in self.stations):
            data.append((s, r))
            if r[status'] == 'ok':
                self.series[s]['minute'][self.fromtimestamp(r['timestamp'])] = r
            data.append((s + '/minute', self.series[s]['minute'].records())
        return data

    def publish(self, data):
        for parameter, record in data:
            self.rxtxapi.publish('weather_stations/' + parameter, record)
        return data

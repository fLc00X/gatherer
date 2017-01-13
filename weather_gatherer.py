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
                result[parameter] = str(root.find(self.parameters[parameter]).text)
            result['status'] = 'ok'
        return result

    def collect(self):
        return [self.readStation(station, name) for station, name in self.stations]

    def publish(self, data):
        for d in data:
            self.rxtxapi.publish('weather_stations/' + d['station'], d)
        return data

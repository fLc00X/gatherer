#!/bin/python

import base_gatherer
from rxtxapi import readUrl

class AqiGatherer(base_gatherer.BaseGatherer):
    def __init__(self, interval, rxtxapi, url, stations):
        super(AqiGatherer, self).__init__(interval, rxtxapi)
        self.url = url
        self.stations = stations

    def readStation(self, station, name):
        result = {'station': station,
                  'name': name,
                  'status': 'error',
                  'timestamp': self.timestamp(),
                  'ozone': -1.00,
                  'pollution': -1.00}
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
                                                  .trim())
            result['status'] = 'ok'
        return result

    def collect(self):
        return [self.readStation(station, name) for station, name in self.stations]

    def publish(self, data):
        for d in data:
            self.rxtxapi.publish('aqi_stations/' + d['station'], d)
return data

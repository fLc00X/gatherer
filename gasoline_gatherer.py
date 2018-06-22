#!/bin/python

import base_gatherer
from rxtxapi import readUrl

class GasolineGatherer(base_gatherer.BaseGatherer):
    def __init__(self, interval, rxtxapi, url, stations):
        super(GasolineGatherer, self).__init__(interval, rxtxapi)
        self.url = url
        self.stations = stations

    def readStation(self, station, name):
        result = {'station': station,
                  'name': name,
                  'status': 'error',
                  'timestamp': self.timestamp()}
        grades = ['regular', 'midgrade', 'premium']
        for grade in grades:
            result[grade] = -1.0
        code, data = readUrl(url = self.url + '/' + station,
                             headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11'})
        if code == 200:
            index = 0
            for line in data.split('<'):
                if 'styles__price___1wJ_R">' in line:
                    if '$' in line and index < len(grades):
                        result[grades[index]] = line.split('$')[1]
                    index += 1
            result['status'] = 'ok'
        return result

    def collect(self):
        return [self.readStation(station, name) for station, name in self.stations]

    def publish(self, data):
        for d in data:
            self.rxtxapi.publish('gas_stations/' + d['station'], d)
        return data

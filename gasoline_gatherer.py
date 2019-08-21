#!/bin/python

import base_gatherer
import datetime
from rxtxapi import readUrl

class GasolineGatherer(base_gatherer.BaseGatherer):
    def __init__(self, interval, rxtxapi, url, stations):
        super(GasolineGatherer, self).__init__(interval, rxtxapi)
        self.url = url
        self.stations = stations

    def parseGrade(self, line):
        for id, grade in enumerate(['">Regular', '">Midgrade', '">Premium']):
            if grade in line:
                return id
        return -1

    def parsePrice(self, line):
        pattern = 'FuelTypePriceDisplay__price___3iizb">'
        if '$' in line and pattern in line and len(line.split(pattern)[1]) > 0:
            return line.split('$')[1]
        return -1.0

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
                _index = self.parseGrade(line)
                if _index != -1:
                    index = _index
                    continue
                price = self.parsePrice(line)
                if result[grades[index]] == -1.0 and price > 0:
                    result[grades[index]] = price
            result['status'] = 'ok'
        else:
            result['errorCode'] = code
        return result

    def date(self):
        return datetime.datetime.now().strftime('%Y-%m-%d')

    def collect(self):
        return [self.readStation(station, name) for station, name in self.stations]

    def publish(self, data):
        for d in data:
            self.rxtxapi.publish('gas_stations/' + d['station'], d)
            self.rxtxapi.publish('/'.join(['gas_stations',
                                           d['station'],
                                           self.date()]), d)
        return data

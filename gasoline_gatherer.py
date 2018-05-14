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
                  'timestamp': self.timestamp(),
                  'regular': -1.00,
                  'midgrade': -1.00,
                  'premium': -1.00}
        code, data = readUrl(url = self.url + '/' + station,
                             headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11'})
        if code == 200:
            prices = []
            for line in data.split('<'):
                if 'ui header styles__price___1wJ_R' in line and '$' in line:
                    prices.append(line.split('$')[1])
            result['status'] = 'ok'
            result['regular'] = prices[0] if len(prices) >= 1 else -1.00
            result['midgrade'] = prices[1] if len(prices) >= 2 else -1.00
            result['premium'] = prices[2] if len(prices) >= 3 else -1.00
        return result

    def collect(self):
        return [self.readStation(station, name) for station, name in self.stations]

    def publish(self, data):
        for d in data:
            self.rxtxapi.publish('gas_stations/' + d['station'], d)
        return data

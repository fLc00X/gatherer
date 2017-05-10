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
        code, data = readUrl(self.url + '/' + station)
        if code == 200:
            prices = []
            for line in data.split('\n'):
                if '<div class="price-display' in line:
                    if 'credit-price' in line:
                        prices.append(line.split('>')[1].split('<')[0])
                    else:
                        prices.append(-1.00)
            result['status'] = 'ok'
            result['regular'] = prices[1] if len(prices) > 1 else -1.00
            result['midgrade'] = prices[3] if len(prices) > 3 else -1.00
            result['premium'] = prices[5] if len(prices) > 5 else -1.00
        else:
            print 'gasoline_gatherer|readUrl error:' + str(code) + ',' + data
        return result

    def collect(self):
        return [self.readStation(station, name) for station, name in self.stations]

    def publish(self, data):
        for d in data:
            self.rxtxapi.publish('gas_stations/' + d['station'], d)
        return data

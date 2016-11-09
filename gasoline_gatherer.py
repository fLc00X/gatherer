#!/bin/python

import base_gatherer

class GasolineGatherer(base_gatherer.BaseGatherer):
      def __init__(self, interval, rxtxapi, url, stations):
          super(GasolineGatherer, self).__init__(interval, rxrxapi)
          self.url = url
          self.stations = []

      def readStation(self, station, name):
          code, data = self.readUrl(self.url + '/' + station)
          if code == 200:
              prices = []
              for line in data.split('\n'):
                  if '<div class="price-display' in line:
                      if 'credit-price' in line:
                          prices.append(line.split('>')[1].split('<')[0])
                      else:
                          prices.append(-1.00)
              return {'station': station,
                      'name': name,
                      'status': 'ok',
                      'timestamp': self.timestamp(),
                      'regular': prices[1] if len(prices) > 0 else -1.00,
                      'midgrade': prices[3] if len(prices) > 1 else -1.00,
                      'premium':  prices[5] if len(prices) > 2 else -1.00}
          else:
              return {'station': station,
                      'name': name,
                      'status': 'error',
                      'timestamp': self.timestamp(),
                      'regular': -1.00,
                      'midgrade': -1.00,
                      'premium': -1.00}

      def collect(self):
          return [self.readStation(station, name) for station, name in self.stations]

      def publish(self, data):
          for d in data:
              self.rxtxapi.publish('gas_stations/' + d['station'], d)
          return data

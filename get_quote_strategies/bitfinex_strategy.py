# -*- coding: utf-8 -*-

from get_quote_strategies.base import *
from bitfinex.client import Client

class BitfinexStrategy(GetQuoteStrategyBase):

    def get_quotes(self, isin):
        price, date = None, None
        try:
            client = Client()
            ticker = client.ticker(isin)
            logging.debug('ticker = %s', ticker)
            price = ticker['last_price']
            date = datetime.datetime.fromtimestamp(ticker['timestamp'])
        except:
            logging.exception('Failed to get quote for %s', isin)
            raise

        return price, date

    def get_currency_code(self):
        return 'USD'

    def get_table_name(self):
        return 'Cryptocurrencies'

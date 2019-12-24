# -*- coding: utf-8 -*-

from get_quote_strategies.base import *
import xlrd
import urllib.request, urllib.parse, urllib.error

class InvestfundsStrategy(GetQuoteStrategyBase):

    def _get_quote_investfunds(self, isin):
        dateformat = '%d.%m.%Y'
        template_url = "https://investfunds.ru/funds/%s/?date_start=%s&date_end=%s&fund_id=%s&file_name=report&action=excelSave"
        finish_date = datetime.date.today()
        start_date = finish_date - datetime.timedelta(days=14)
        url = template_url % (isin,
                              start_date.strftime(dateformat),
                              finish_date.strftime(dateformat),
                              isin)
        logging.debug('url = %s', url)
        file_name, headers = urllib.request.urlretrieve(url)

        logging.debug('file_name = %s', file_name)
        logging.debug('headers = %s', headers)
        wb = xlrd.open_workbook(file_name)
        sh = wb.sheet_by_index(0)
        date = datetime.datetime(*xlrd.xldate_as_tuple(sh.cell_value(rowx=1, colx=0), wb.datemode))
        price = sh.cell_value(rowx=1, colx=1)
        logging.debug('price = %s; date = %s', price, date)
        return price, date

    def get_quotes(self, isin):
        price, date = None, None
        try:
            price, date = self._get_quote_investfunds(isin)
        except:
            logging.exception('Failed to get quote for %s', isin)

        return price, date

    def get_currency_code(self):
        return 'RUB'

    def get_table_name(self):
        return 'FUND'

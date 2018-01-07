# -*- coding: utf-8 -*-

from get_quote_strategies.base import *
from xlrd import open_workbook
import urllib

class InvestfundsStrategy(GetQuoteStrategyBase):
    
    def _get_quote_investfunds(self, isin):
        url = "http://pif.investfunds.ru/funds/export_to_excel.php?f2[0]=%s&export=2&export_type=xls&start_day=%s&start_month=%s&start_year=%s&finish_day=%s&finish_month=%s&finish_year=%s&rnd=4064','neww2884'"
        finish_date = datetime.date.today()
        start_date = finish_date - datetime.timedelta(days=14)
        logging.debug('url = %s', url)
        logging.debug('start_date = %s; finish_date = %s', start_date, finish_date)
        file_name, headers = urllib.urlretrieve(url % (isin, start_date.day,
                                                           start_date.month,
                                                           start_date.year,
                                                           finish_date.day,
                                                           finish_date.month,
                                                           finish_date.year))

        logging.debug('file_name = %s', file_name)
        logging.debug('headers = %s', headers)
        wb = open_workbook(file_name)
        sh = wb.sheet_by_index(0)
        date = sh.cell_value(rowx=3, colx=0)
        price = sh.cell_value(rowx=3, colx=1)
        logging.info('isin: %s, price: %s, date: %s', isin, price, date)
        return price, date

    def get_quotes(self, isin):
        price, date = None, None
        try:
            price, date = self._get_quote_investfunds(isin)
            date = datetime.datetime.strptime(date, '%d.%m.%Y')
        except:
            logging.exception('Failed to get quote for %s', isin)
            raise

        return price, date

    def get_currency_code(self):
        return 'RUB'

    def get_table_name(self):
        return 'FUND'

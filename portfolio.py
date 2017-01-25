#!/usr/bin/env python
# -*- coding: utf-8 -*-

from argparse import ArgumentParser
import datetime
import logging
import requests
import urllib

from xlrd import open_workbook
from bs4 import BeautifulSoup
from gnucash import Session, GncNumeric, GncPrice, ACCT_TYPE_STOCK

from fractions import Fraction

def get_quote_onvista_bond(isin):
    url = 'http://www.onvista.de/anleihen/snapshot.html?ISIN={}'.format(isin)
    r = requests.get(url)
    soup = BeautifulSoup(r.text)
    price = soup.select('.INHALT #KURSINFORMATIONEN ~ .t span:nth-of-type(2)')[0].get_text()
    currency = 'EUR'
    logging.info('Got quote for %s: %s%%', isin, price)
    return GncNumeric(int(price.replace(',', '')), 100 * 100), currency


def get_quote_onvista_stock(isin):
    url = 'http://www.onvista.de/suche/?searchValue={}'.format(isin)
    r = requests.get(url)
    soup = BeautifulSoup(r.text)
    spans = soup.select('.INHALT ul.KURSDATEN li:nth-of-type(1) span')
    price = spans[0].get_text()
    currency = str(spans[1].get_text())
    logging.info('Got quote for %s: %s %s', isin, price, currency)
    return GncNumeric(int(price.replace(',', '')), 1000), currency


def get_quote_investfunds(isin):
    url = "http://pif.investfunds.ru/funds/export_to_excel.php?f2[0]=%s&export=2&export_type=xls&start_day=%s&start_month=%s&start_year=%s&finish_day=%s&finish_month=%s&finish_year=%s&rnd=4064','neww2884'"
    finish_date = datetime.date.today()
    start_date = finish_date - datetime.timedelta(days=7)
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

def update_quote(commodity, book):
    fullname = commodity.get_fullname()
    mnemonic = commodity.get_mnemonic()
    isin = commodity.get_cusip()
    if isin is None:
        return
    logging.info('Processing %s (%s, %s)..', fullname, mnemonic, isin)
    price, date = None, None
    try:
        price, date = get_quote_investfunds(isin)
        date = datetime.datetime.strptime(date, '%d.%m.%Y')
    except:
        logging.exception('Failed to get quote for %s', isin)

    if price and date:
        table = book.get_table()
        gnc_commodity = table.lookup('FUND', mnemonic)
        gnc_currency = table.lookup('CURRENCY', 'RUB')

        pricedb = book.get_price_db()
        pl = pricedb.get_prices(gnc_commodity, gnc_currency)
        if len(pl) < 1:
            logging.exception('Need price entry in DB')
            return

        p = pl[0].clone(book)
        p = GncPrice(instance = p)
        p.set_time(date)
        v = p.get_value()
        v.num = int(Fraction.from_float(float(price)).limit_denominator(100000).numerator)
        v.denom = int(Fraction.from_float(float(price)).limit_denominator(100000).denominator)
        p.set_value(v)

        book.get_price_db().add_price(p)


def update_quotes(s, args):
    book = s.book
    table = book.get_table()
    for namespace in table.get_namespaces_list():
        name = namespace.get_name()
        if name == 'FUND':
            for commodity in namespace.get_commodity_list():
                update_quote(commodity, book)
    if not args.dry_run:
        s.save()


def report(s, args):
    book = s.book
    table = book.get_table()
    pricedb = book.get_price_db()
    # FIXME: hard-coded currency
    currency_code = 'EUR'
    currency = table.lookup('ISO4217', currency_code)
    account = book.get_root_account()
    for acc in account.get_descendants():
        if acc.GetType() == ACCT_TYPE_STOCK:
            commodity = acc.GetCommodity()
            namespace = commodity.get_namespace()
            if namespace != 'CURRENCY':
                print commodity.get_fullname(), commodity.get_cusip(), acc.GetBalance()
                inst = pricedb.lookup_latest(commodity, currency).get_value()
                print GncNumeric(instance=inst).to_string()


def parse_arguments():
    parser = ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group()
    group.add_argument('-v', '--verbose', help='Verbose (debug) logging', action='store_const', const=logging.DEBUG,
                       dest='loglevel')
    group.add_argument('-q', '--quiet', help='Silent mode, only log warnings', action='store_const',
                       const=logging.WARN, dest='loglevel')
    parser.add_argument('--dry-run', help='Noop, do not write anything', action='store_true')
    parser.add_argument('-isin', nargs='?', help='Mutual fund isin')
    parser.add_argument('book', help='gnucash file')

    args = parser.parse_args()
    return args

if __name__ == "__main__":
    args = parse_arguments()
    logging.basicConfig(level=args.loglevel or logging.INFO)
    logging.debug(args)

    if args.isin:
        price, date = get_quote_investfunds(args.isin)

    s = Session(args.book)
    try:
        update_quotes(s, args)
    finally:
        s.end()

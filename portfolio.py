#!/usr/bin/env python
# -*- coding: utf-8 -*-

from argparse import ArgumentParser
import logging

from gnucash import Session, GncNumeric, GncPrice, ACCT_TYPE_STOCK

from fractions import Fraction

from get_quote_strategies.investfunds import InvestfundsStrategy
from get_quote_strategies.bitfinex_strategy import BitfinexStrategy

from statistics import get_delta, show_delta

get_quote_strategies = [InvestfundsStrategy(), BitfinexStrategy()]

def update_quote(commodity, book, get_quote_strategy):
    fullname = commodity.get_fullname()
    mnemonic = commodity.get_mnemonic()
    isin = commodity.get_cusip()
    if isin is None:
        return
    logging.info('')
    logging.info('Processing %s (%s, %s)..', fullname, mnemonic, isin)
    price, date = get_quote_strategy.get_quotes(isin)
    logging.info('New price: %s, price: %s, date: %s', mnemonic, price, date)

    if price and date:
        table = book.get_table()
        gnc_commodity = table.lookup(get_quote_strategy.get_table_name(), mnemonic)
        gnc_currency = table.lookup('CURRENCY', get_quote_strategy.get_currency_code())

        pricedb = book.get_price_db()
        pl = pricedb.get_prices(gnc_commodity, gnc_currency)
        if len(pl) < 1:
            logging.exception('Need price entry in DB')
            return
        else:
            v = pl[0].get_value()
            last_price = 1.0*v.num/v.denom
            logging.info('Last price: %f', last_price)
            show_delta(get_delta(last_price, price))

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
        for commodity in namespace.get_commodity_list():
            for strategy in get_quote_strategies:
                if name == strategy.get_table_name():
                    update_quote(commodity, book, strategy)
                    break
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

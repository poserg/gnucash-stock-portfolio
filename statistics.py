# -*- coding: utf-8 -*-
import logging

from termcolor import colored

from math import ceil

def get_delta(last_price, new_price):
    logging.debug('last_price = %s; new_price = %s', last_price, new_price)

    delta = ceil(10000.0*(new_price - last_price)/last_price)/100
    logging.debug('delta = %f', delta)
    return delta

def show_delta(delta):
    s = str(delta) + ' %'
    c = 'yellow'
    if delta > 0:
        s = '+' + s
        c = 'green'
    elif delta < 0:
        s = s
        c = 'red'
    print 'delta: ' + colored(s, c)

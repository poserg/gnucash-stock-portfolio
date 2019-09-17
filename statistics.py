# -*- coding: utf-8 -*-
import logging

from termcolor import colored

from math import ceil

def get_delta(last_price, new_price):
    logging.debug('last_price = %s; new_price = %s', last_price, new_price)

    abs_delta = new_price - last_price
    delta = ceil(10000.0*(abs_delta)/last_price)/100
    logging.debug('delta = %f', delta)
    return abs_delta, delta

def show_delta(delta):
    abs_delta_s = str(delta[0])
    delta_s = str(delta[1]) + ' %'
    c = 'yellow'
    if delta[0] > 0:
        abs_delta_s = '+' + abs_delta_s
        delta_s = '+' + delta_s
        c = 'green'
    elif delta[0] < 0:
        c = 'red'
    print('delta: ' + colored('%s (%s)' % (abs_delta_s, delta_s), c))

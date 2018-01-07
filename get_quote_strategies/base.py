# -*- coding: utf-8 -*-

import datetime
import logging

class GetQuoteStrategyBase:

    def get_quotes(self, isin):
        raise NotImplementedError

    def get_currency_code(self):
        raise NotImplementedError

    def get_table_name(self):
        raise NotImplementedError

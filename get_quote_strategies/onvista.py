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



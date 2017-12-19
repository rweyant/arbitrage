import ccxt
import pandas as pd
from settings import *


def get_binance_client():
    binance = ccxt.binance()
    binance.apiKey = binance_key
    binance.secret = binance_secret

    return binance


def get_poloniex_client():
    poloniex = ccxt.poloniex()
    poloniex.apiKey = polo_key
    poloniex.secret = polo_secret

    return poloniex


def get_gdax_client():
    gdax = ccxt.gdax()
    gdax.apiKey = gdax_key
    gdax.password = gdax_passphrase
    gdax.secret = gdax_secret

    return gdax


def get_prices(client, suffix, gdax=False):
    # client, suffix = b, 'g'
    if not gdax:
        tickers = client.fetch_tickers()
    else:
        tickers = {'ETH/BTC': client.fetch_ticker(symbol='ETH/BTC'),
                   'LTC/BTC': client.fetch_ticker(symbol='LTC/BTC')}

    lst = []
    for k in tickers.keys():
        lst.append({'symbol': tickers[k]['symbol'],
                    'ask_' + suffix: tickers[k]['ask'],
                    'bid_' + suffix: tickers[k]['bid'],
                    'top': tickers[k]['symbol'].split('/')[0],
                    'bottom': tickers[k]['symbol'].split('/')[1]})

    return pd.DataFrame(lst)


def combine_prices(x, y):
    # x, y = b_prices, p_prices
    # suffix_x, suffix_y = 'b', 'p'
    suffix_x = [x for x in x.columns if 'ask' in x][0].split('_')[1]
    suffix_y = [x for x in y.columns if 'ask' in x][0].split('_')[1]
    combined_prices = pd.merge(x, y, on=['symbol', 'top', 'bottom'])

    # Bid is sale price, ask is buy price
    b_x, a_x = 'bid_{}'.format(suffix_x), 'ask_{}'.format(suffix_x)
    b_y, a_y = 'bid_{}'.format(suffix_y), 'ask_{}'.format(suffix_y)
    x_to_y, y_to_x = 'bid_{}_to_ask_{}'.format(suffix_x, suffix_y), 'bid_{}_to_ask_{}'.format(suffix_y, suffix_x)

    combined_prices.loc[:, x_to_y] = combined_prices.loc[:, b_x] / combined_prices.loc[:, a_y]
    combined_prices.loc[:, y_to_x] = combined_prices.loc[:, b_y] / combined_prices.loc[:, a_x]

    combined_prices.loc[:, suffix_x] = combined_prices.loc[:, x_to_y].apply(lambda x: 'sell' if x > 1 else 'buy')
    combined_prices.loc[:, suffix_y] = combined_prices.loc[:, y_to_x].apply(lambda x: 'sell' if x > 1 else 'buy')
    # combined_prices.loc[:, y_to_x].apply(lambda x: 'sell y buy x' if x > 1 else '')

    combined_prices = combined_prices.loc[combined_prices.top != 'STORJ']
    combined_prices = combined_prices.loc[combined_prices.top != 'GAS']

    if max(combined_prices.loc[:, x_to_y]) > max(combined_prices.loc[:, y_to_x]):
        return combined_prices.loc[combined_prices.loc[:, x_to_y] > 1].sort_values(x_to_y, ascending=False)
        # return combined_prices.sort_values(x_to_y, ascending=False)
    else:
        return combined_prices.loc[combined_prices.loc[:, y_to_x] > 1].sort_values(y_to_x, ascending=False)
        # return combined_prices.sort_values(y_to_x, ascending=False)

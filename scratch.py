from utils import *
import pandas as pd
from time import sleep
import datetime
import logging

p = get_poloniex_client()
b = get_binance_client()
g = get_gdax_client()

p_prices = get_prices(p, suffix='p')
b_prices = get_prices(b, suffix='b')
g_prices = get_prices(g, suffix='g', gdax=True)

combined_prices = combine_prices(p_prices, b_prices)
combined_prices = combine_prices(b_prices, g_prices)



# Bid is sale price, ask is buy price
top_trade = combined_prices.head(1)
top_trade
trade_dict = top_trade.reset_index().to_dict()

# Identify symbols and prices for this iteration
symbol = trade_dict['symbol'][0]
top = trade_dict['top'][0]
bottom = trade_dict['bottom'][0]
buy_price = trade_dict['ask_p'][0]
sell_price = trade_dict['bid_b'][0]

# Determine how much to buy this iteration
bottom_quantity = 0.001 # p.fetch_balance()[bottom]['free']
amount_to_buy = bottom_quantity / sell_price

print('''{symbol}\npoloniex action:*{p}*\tbinance action:*{b}*'''.format(symbol=symbol, p=trade_dict['p'][0], b=trade_dict['b'][0]))
print('''Sell {}\npoloniex action:*{p}*\tbinance action:*{b}*'''.format(symbol=symbol, p=trade_dict['p'][0], b=trade_dict['b'][0]))

# ACTUALLY WILL MAKE ORDERS #

def blocking_single_iteration(buyer, seller, buy_price, sell_price, symbol):
    top = symbol.split('/')[0]
    bottom = symbol.split('/')[1]

    # WLOG assume buy in p, sell in b

    # Make the buy order
    buy_order = buyer.create_limit_buy_order(symbol, amount_to_buy, buy_price)

    if buyer.fetch_order(buy_order['id'])['status'] == 'closed':

        # Once the order goes through, transfer all of it to b
        withdraw_id = p.withdraw(top, p.fetch_balance()[top]['free'], b.fetch_deposit_address(top)['address'])
        p.fetch_fees(symbol='STRAT')
        start = datetime.datetime.now()
        while b.fetch_balance()[top]['free'] == 0:
            sleep(60)
        print('Withdrawal took {} seconds'.format((datetime.datetime.now() - start).total_seconds()))

        # Once the transfer is done, sell all of it at b
        amount_to_sell = b.fetch_balance()[top]['free']
        sell_order = b.create_limit_sell_order(symbol, amount_to_sell, sell_price)

        if b.fetch_order(sell_order['id'])['status'] == 'closed':
            withdraw_id = b.withdraw(top, b.fetch_balance()[bottom]['free'], p.fetch_deposit_address(bottom)['address'])


# WLOG assume buy in p, sell in b

# Make the buy order
buy_order = p.create_limit_buy_order(symbol, amount_to_buy, buy_price)

if p.fetch_order(buy_order['id'])['status'] == 'closed':

    # Once the order goes through, transfer all of it to b
    withdraw_id = p.withdraw(top, p.fetch_balance()[top]['free'], b.fetch_deposit_address(top)['address'])
    p.fetch_fees(symbol='STRAT')
    start = datetime.datetime.now()
    while b.fetch_balance()[top]['free'] == 0:
        sleep(60)
    print('Withdrawal took {} seconds'.format((datetime.datetime.now() - start).total_seconds()))


    # Once the transfer is done, sell all of it at b
    amount_to_sell = b.fetch_balance()[top]['free']
    sell_order = b.create_limit_sell_order(symbol, amount_to_sell, sell_price)

    if b.fetch_order(sell_order['id'])['status'] == 'closed':
        withdraw_id = b.withdraw(top, b.fetch_balance()[bottom]['free'], p.fetch_deposit_address(bottom)['address'])


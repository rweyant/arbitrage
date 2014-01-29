#####################
# ARBITRAGE PROJECT #
#####################

This script currently looks at arbitrage opportunites between crypto-trade and BTC-e exchanges.
More exchanges to be added.  More currencies per exchange too -- this only includes a small
sample of currencies offered by each exchange.

It uses a map algorithm/class to traverse all possible paths from input currency-exchange pair to
output currency-exchange pair.  It retrieves current exchange rates for all currencies listed
and assumes a .2% fee per transaction.

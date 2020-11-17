from __future__ import (absolute_import, division, print_function, unicode_literals)

import datetime  # For datetime objects
import os.path  # To manage paths
import sys  # To find out the script name (in argv[0])
import backtrader as bt
from strategies import buycross
#from bbadx import BBADX



if __name__ == '__main__':
    # Create a cerebro entity
    cerebro = bt.Cerebro()
    
    # Create a Data Feed
    data = bt.feeds.YahooFinanceCSVData(
        dataname='qqq.csv',
        # Do not pass values before this date
        fromdate= datetime.datetime(2019, 10, 4),
        # Do not pass values after this date
        todate= datetime.datetime(2020, 10, 4),
        reverse=False)
    
    # Add the Data Feed to Cerebro
    cerebro.adddata(data)

    # Set the starting cash
    cerebro.broker.setcash(100000.0)

    # Set the commission - 0.1% ... divide by 100 to remove the %
    cerebro.broker.setcommission(commission=0.001)

    # Select the strategy from strategies.py
    cerebro.addstrategy(buycross)

    # Set default position size
    cerebro.addsizer(bt.sizers.FixedSize, stake=1000)

    print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())

    cerebro.run()  

    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())

    cerebro.plot()
import backtrader as bt
import datetime

# Create a Strategy
class buycross(bt.Strategy):

    def log(self, txt, dt=None):
        #''' Logging function fot this strategy'''
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self):
        # Keep a reference to the "close" line in the data[0] dataseries
        self.dataclose = self.datas[0].close

        # To keep track of pending orders and buy price/commission
        self.order = None
        self.buyprice = None
        self.buycomm = None
        self.mklong = None
        self.mkshort = None


        # Add a quick and slow MovingAverageSimple indicator
        self.sma = bt.indicators.MovingAverageSimple(self.datas[0], period=30)
        

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            # Buy/Sell order submitted/accepted to/by broker - Nothing to do
            return

        # Check if an order has been completed
        # Attention: broker could reject order if not enough cash
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(
                    'BUY EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' %
                    (order.executed.price,
                     order.executed.value,
                     order.executed.comm))

                self.buyprice = order.executed.price
                self.buycomm = order.executed.comm
            else:  # Sell
                self.log('SELL EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' %
                         (order.executed.price,
                          order.executed.value,
                          order.executed.comm))

            self.bar_executed = len(self)

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')

        self.order = None

    def notify_trade(self, trade):
        if not trade.isclosed:
            return

        self.log('OPERATION PROFIT, GROSS %.2f, NET %.2f' %
                 (trade.pnl, trade.pnlcomm))

    def next(self):
        # Simply log the closing price of the series from the reference
        self.log('Close, %.2f' % self.dataclose[0])

        # Check if an order is pending ... if yes, we cannot send a 2nd one
        if self.order:
            return

        nowMA = self.sma[0]
        nowClose = self.dataclose[0]
        previousMA= self.sma[-1]
        previousClose = self.dataclose[-1]
    
        # Define crossovers for the point in time strategy
        upward_crossover = previousClose < previousMA and nowClose > nowMA
        downward_crossover = previousClose > previousMA and nowClose < nowMA

        # Check if we are in the market
        if not self.position:
            # Confirm we're NOT in the market
            
            if upward_crossover:

                # BUY, BUY, BUY!!! (with default parameters)
                self.log('OPEN LONG, %.2f' % self.dataclose[0])

                # Keep track of the created order to avoid a 2nd order
                self.order = self.buy()

                # Keep track of the fact that we're long in the market
                self.mklong = True
            
            if downward_crossover:

                # SELL SHORT
                self.log('OPEN SHORT, %.2f' % self.dataclose[0])

                # Keep track of the created order to avoid a 2nd order
                self.order = self.sell()

                # Keep track of the fact that we're short in the market
                self.mkshort = True


        else:
            # Confirm we ARE in the market

            if downward_crossover and self.mklong == True:

                # SELL, SELL, SELL!!! (with all possible default parameters)
                self.log('CLOSE LONG, %.2f' % self.dataclose[0])

                # Keep track of the created order to avoid a 2nd order
                self.order = self.sell()

                mklong = False

            
            if upward_crossover and self.mkshort == True:

                # BUY, BUY, BUY!!! (with default parameters)
                self.log('CLOSE SHORT, %.2f' % self.dataclose[0])

                # Keep track of the created order to avoid a 2nd order
                self.order = self.buy()

                self.mkshort = False

import backtrader as bt
import backtrader.indicators as btind
import datetime


#create a class
class TestStrat(bt.Strategy):


    def log(self, txt, dt=None):
        #''' Logging function fot this strategy'''
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self):

        #keep a log of where we are in the datafeed
        self.dataclose = self.datas[0].close
        
        #create fast and slow moving averages
        self.ma_fast = btind.SMA(period = 5)
        self.ma_slow = btind.SMA(period = 30)
        # set values for when the fast ma crosses the slow w backtrader's indicator
        self.crossover = btind.CrossOver(self.ma_fast, self.ma_slow)

    def notify_order(self, order):
        # check the status       
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log('BUY, %.2f' % self.dataclose[0])
            else:
                self.log('SELL, %.2f' % self.dataclose[0])
        
        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')

    def notify_trade(self, trade):
        if not trade.isclosed:
            return

        self.log('OPERATION PROFIT, GROSS %.2f, NET %.2f' % (trade.pnl, trade.pnlcomm))

    def next(self):

        if not self.position:
            if self.ma_fast > self.ma_slow:
                self.buy()
        
            elif self.ma_fast < self.ma_slow:
                self.sell()
        
        if self.position:         
            if self.crossover > 0:
                self.close()
                self.buy()
        
            elif self.crossover < 0:
                self.close()
                self.sell()

   
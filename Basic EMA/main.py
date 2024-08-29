# region imports
from AlgorithmImports import *
# endregion

class FatYellowGreenAnguilline(QCAlgorithm):

    def Initialize(self):
        self.set_start_date(2023, 12, 29)
        self.set_end_date(2024, 1, 1)
        self.set_cash(1000000)
        self.SetBenchmark(Symbol.Create("BTCUSDT", SecurityType.Crypto, Market.Binance))
        #add security
        self.crypto = self.add_crypto('BTCUSDT', Resolution.SECOND).Symbol
        #set brokerage model
        #self.set_brokerage_model(BrokerageName.COINBASE, AccountType.CASH)
        self.baseEMA = 1
        self.EMAlis = []
        period = 5
        self.Schedule.On(self.DateRules.EveryDay(), self.TimeRules.Every(TimeSpan.FromSeconds(period)), self.CalcEMA)


    def CalcEMA(self):
        price = self.securities[self.crypto].price
        #smoothing factor = 2 and period = 5 seconds
        period = 5
        smoothing = 2
        #EMA CALC
        EMA = price*(smoothing/(1+period))+self.baseEMA*(1-(smoothing/(1+period)))
        self.baseEMA = EMA
        self.EMAlis.append(EMA)


    def on_data(self, data = Slice):
        self.CalcEMA()
        if len(self.EMAlis) > 3:
            self.EMAlis.pop(0)
            if not self.portfolio.Invested and self.EMAlis[-1] > self.EMAlis[-2] > self.EMAlis[0]:
                self.set_holdings(self.crypto, .2)
            #elif self.securities[self.crypto].price < self.transactions.get_order_by_id(self.transactions.last_order_id).price:
                #self.set_holdings(self.crypto, 0)
            elif self.EMAlis[-1] < self.EMAlis[-2] < self.EMAlis[0]:
                self.set_holdings(self.crypto, 0)

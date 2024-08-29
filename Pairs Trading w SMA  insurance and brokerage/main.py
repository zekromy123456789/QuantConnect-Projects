#I wanted to make this project because i believe that insurance brokerage and insurance are pretty correlated
#i chose AJG (Brokerage) and UNH (Insurer) as my 2 equities
#Some areas i could improve on include automatic stock selection and more in depth indicators
#Results for given Dates:
#Total Equity at end period: 137,019.13
#Total Fees: -$1,291.55
#Net Profits: $37,019.13
#PSR: 80.974%
#Return: 37.02%

# region imports
from AlgorithmImports import *
from datetime import timedelta, datetime
# endregion

class PairsTradingwSMA(QCAlgorithm):

    def initialize(self):
        self.set_start_date(2022, 1, 1)
        self.set_end_date(2023, 12, 31)
        self.set_cash(100000)
        #add symbols
        symbols = [Symbol.Create("AJG", SecurityType.Equity, Market.USA), Symbol.Create("UNH", SecurityType.Equity, Market.USA)]
        #create new instance of universe
        self.AddUniverseSelection(ManualUniverseSelectionModel(symbols))
        #change universe settings
        self.universe_settings.resolution = Resolution.Hour
        self.universe_settings.data_normalization_mode = DataNormalizationMode.RAW
        self.add_alpha(PairsTradingAlphaModel())
        self.set_portfolio_construction(EqualWeightingPortfolioConstructionModel())
        self.set_execution(ImmediateExecutionModel())

        #log positions at the end of each trading day
        def on_end_of_day(self, symbol):
            self.Log("Taking a position of " +str(self.Portfolio[symbol].Quantity) + " units of symbol " + str(symbol))

class PairsTradingAlphaModel(AlphaModel):
    def __init__(self):
        #list that holds symbol pair
        self.pair = []
        #create SMA indicator monitoring spread
        #base 500 bar moving average
        self.spreadMean = SimpleMovingAverage(500)
        #create Standard Deviation indicator monitoring spread
        #base 500 bar Standard Deviation
        self.spreadStd = StandardDeviation(500)
        #set self.period
        #base 2 hour dela
        self.period = timedelta(hours=2)

    def update(self, algorithm, data):
        spread = self.pair[1].Price - self.pair[0].Price
        #update indicators with spread
        self.spreadMean.Update(algorithm.Time, spread)
        self.spreadStd.Update(algorithm.Time, spread)
        #save threshholds
        upperthreshold = self.spreadMean.Current.Value + self.spreadStd.Current.Value
        lowerthreshold = self.spreadMean.Current.Value - self.spreadStd.Current.Value

        # if spread > upper thresh emit an Insight.Group()
        if spread > upperthreshold:
            return Insight.Group([
                    Insight.Price(self.pair[0].Symbol,self.period, InsightDirection.Up),
                    Insight.Price(self.pair[1].Symbol,self.period, InsightDirection.Down)
                ])
        #if spread < lower thresh emit an Insight.Group()
        if spread < lowerthreshold:
            return Insight.Group([
                    Insight.Price(self.pair[0].Symbol,self.period, InsightDirection.Down),
                    Insight.Price(self.pair[1].Symbol,self.period, InsightDirection.Up)
                ])
        #if spread is in between don't do anything
        return []

    def OnSecuritiesChanged(self, algorithm, changes):
        self.pair = [x for x in changes.AddedSecurities]
        #call for historical data
        history = algorithm.History([x.Symbol for x in self.pair], 500)
        history = history.close.unstack(level=0)
        #iterate through history tuple and update indicators
        for tuple in history.itertuples():
            self.spreadMean.Update(tuple[0], tuple[2]-tuple[1])
            self.spreadStd.Update(tuple[0], tuple[2]-tuple[1])

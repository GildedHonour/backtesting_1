import pandas as pd
from backtesting import Backtest, Strategy
from backtesting.lib import crossover
from backtesting.test import GOOG

class Strategy1(Strategy):
    def init(self):
        self.atr_period = 14
        self.stop_loss_factor = 0.5
        self.take_profit_factor = 0.5
        self.in_position = False

        # Convert the closing prices to a pandas.Series object
        close_prices = pd.Series(self.data.Close, index=self.data.index)

        # Calculate ATR
        tr = pd.Series([max(h - l, abs(h - c), abs(l - c)) for h, l, c in zip(self.data.High, self.data.Low, close_prices)], index=self.data.index)
        self.atr = tr.rolling(window=self.atr_period).mean()

        # Calculate EMAs
        self.ma = close_prices.rolling(window=20).mean()
        self.ema = close_prices.ewm(span=20).mean()
        self.dema = 2 * self.ema - self.ema.ewm(span=20).mean()

        # Calculate TEMA
        ema1 = close_prices.ewm(span=20).mean()
        ema2 = ema1.ewm(span=20).mean()
        ema3 = ema2.ewm(span=20).mean()
        self.tema = 3 * (ema1 - ema2) + ema3

    def next(self):
        if self.data.index[-1].date() != self.data.index[-2].date():
            # Exit the position at closing price or opening price of the next day
            self.sell()

        elif not self.in_position:
            # Check for entry conditions
            if (
                self.data.Close[-1] > self.ma[-1]
                and self.data.Close[-1] > self.ema[-1]
                and self.ema[-1] > self.dema[-1]
                and self.dema[-1] > self.tema[-1]
                and crossover(self.data.Close, self.ma)
                and crossover(self.ema, self.dema)
                and crossover(self.dema, self.tema)
            ):
                # Entry at closing price
                self.buy(sl=self.data.Close[-1] - (self.atr[-1] / 2),
                         tp=self.data.Close[-1] + (self.atr[-1] / 2),
                         exectype=bt.Order.Market)
                self.in_position = True

        else:
            # Check for exit conditions
            if (
                crossover(self.ma, self.data.Close)
                or crossover(self.ema, self.data.Close)
                or crossover(self.dema, self.data.Close)
                or crossover(self.tema, self.data.Close)
            ):
                # Exit the position at closing price
                self.sell()

class Backtest1(Backtest):
    def __init__(self):
        super().__init__(
            GOOG,
            Strategy1,
            cash=100000,
            commission=0.0,
            exclusive_orders=True,
            trade_on_close=True
        )

bt = Backtest1()
results = bt.run()
print(results)
bt.plot()

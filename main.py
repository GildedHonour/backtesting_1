import pandas as pd
from backtesting import Backtest, Strategy
from backtesting.lib import crossover
from backtesting.test import GOOG
import yfinance as yf
import pandas as pd

SYMBOLS = ['SPY', 'F', 'AMZN', 'AAPL', 'QQQ', 'BAC', 'T', 'IWM', 'PYPL', 'HYG', 'MSFT', 'GOOGL', 'PFE', 'PBR', 'VALE', 'CSCO', 'BABA', 'META', 'ITUB', 'PCG', 'SYF', 'AAL', 'VZ', 'XOM', 'ORCL', 'EFA', 'GOLD', 'WFC', 'BBD', 'TEVA', 'CMCSA', 'GM', 'VTRS', 'DIS', 'KO']

# adjust the dates if needed
# `yfinance` would have to have them too
data = yf.download(SYMBOLS, start='2022-01-01', end='2023-01-01')


def get_data_frame_by_symbol(sym):
    # convert into the correct format
    srs = []
    for h in ['Open', 'High', 'Low', 'Close', 'Volume']:
      k = (h, sym,)
      srs.append(pd.Series(data[k], name=h))

    return pd.concat(srs, axis=1)


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
    def __init__(self, sym):
        super().__init__(
            # GOOG,
            sym,
            Strategy1,
            cash=100000,
            commission=0.0,
            exclusive_orders=True,
            trade_on_close=True
        )



# 1
# the standard `GOOG` DataFrame imported from `backtesting.test`
# bt = Backtest1(GOOG)

# or
# 2
sym = 'PYPL'
sym_df = get_data_frame_by_symbol(sym)
bt = Backtest1(sym_df)

#
# results
#
results = bt.run()
print(results)
bt.plot()
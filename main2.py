import yfinance as yf
import pandas as pd
from backtesting import Backtest, Strategy
from backtesting.lib import SignalStrategy
import numpy as np
import matplotlib.pyplot as plt

data = yf.download('AMZN', start='2018-01-01', end='2022-12-31')

class MyTema(Strategy):
    def init(self):
        self.tema_values = []

    def next(self):
        if len(self.data.Close) < 3:
            return

        ema1 = np.mean(self.data.Close[-3:])
        ema2 = np.mean(ema1)
        ema3 = np.mean(ema2)
        tema = 3 * (ema1 - ema2) + ema3

        if tema < self.data.Close[-1] and not self.position:
            self.buy()
        elif tema > self.data.Close[-1] and self.position:
            self.position.close()

        self.tema_values.append(tema)  # Store TEMA value

bt = Backtest(data, MyTema)
results = bt.run()

tema_values = results._strategy.tema_values

dates = pd.to_datetime(data.index[-len(tema_values):])

plt.plot(dates, tema_values)

plt.title('Triple Exponential Moving Average (TEMA)')
plt.xlabel('Date')
plt.ylabel('TEMA')

plt.xticks(rotation=45, ha='right')
plt.show()

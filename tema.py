import yfinance as yf
import pandas as pd
from backtesting import Backtest, Strategy
import talib
import matplotlib.pyplot as plt
import mplfinance as mpf

# SYMBOLS = ['SPY', 'F', 'AMZN', 'AAPL', 'QQQ', 'BAC', 'T', 'IWM', 'PYPL', 'HYG', 'MSFT', 'GOOGL', 'PFE', 'PBR', 'VALE', 'CSCO', 'BABA', 'META', 'ITUB', 'PCG', 'SYF', 'AAL', 'VZ', 'XOM', 'ORCL', 'EFA', 'GOLD', 'WFC', 'BBD', 'TEVA', 'CMCSA', 'GM', 'VTRS', 'DIS', 'KO']

# adjust the dates
data = yf.download('AAPL', start='2023-05-01', end='2023-07-07')

class MyTema(Strategy):
    def init(self):
        self.tema_values = []

    def next(self):
        if len(self.data.Close) < 4:
            return

        tema = talib.TEMA(self.data.Close, timeperiod=4)
        self.tema_values.append(tema[-1])

        if self.data.Close[-2] < tema[-2] and self.data.Close[-1] > tema[-1]:
            self.buy()
        elif self.data.Close[-2] > tema[-2] and self.data.Close[-1] < tema[-1] and self.position:
            self.sell()


bt = Backtest(data, MyTema)
results = bt.run()
tema_values = results._strategy.tema_values[-len(data):]

tema_df = pd.DataFrame({'Date': data.index[-len(tema_values):], 'TEMA': tema_values})
tema_df.set_index('Date', inplace=True)

combined_df = pd.concat([data['Open'][-len(tema_values):], data['High'][-len(tema_values):],
                         data['Low'][-len(tema_values):], data['Close'][-len(tema_values):], tema_df], axis=1)

mpl_style = mpf.make_mpf_style(base_mpf_style='classic', rc={'figure.facecolor': 'white'},
                               marketcolors=mpf.make_marketcolors(up='g', down='r'))

mpf.plot(combined_df, type='candle', style=mpl_style, title='Triple Exponential Moving Average (TEMA) and Closing Price',
         ylabel='Price', figscale=1.5, addplot=mpf.make_addplot(tema_df['TEMA'], color='red'),
         scale_width_adjustment=dict(lines=0.3))


plt.show()

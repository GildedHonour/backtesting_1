import pandas as pd
from datetime import datetime
from backtesting import Backtest, Strategy
import talib
import yfinance as yf
import matplotlib.pyplot as plt
import mplfinance as mpf


# Define the start and end dates
start_date = datetime(2023, 5, 1)
end_date = datetime(2023, 7, 31)

# Fetch AAPL historical data from Yahoo Finance using yfinance
data = yf.download('AAPL', start=start_date, end=end_date)

class MyTema(Strategy):
    def init(self):
        self.tema_values = []

    def next(self):
        if len(self.data) < 4:
            return

        tema = talib.TEMA(self.data['Close'], timeperiod=4)
        self.tema_values.append(tema[-1])

        if self.data['Close'][-2] < tema[-2] and self.data['Close'][-1] > tema[-1]:
            self.buy()

        if self.position:
            # Close the position on the next trading day
            self.position.close()




bt = Backtest(data, MyTema)
results = bt.run()

print("trades:", len(results["_trades"]))
print(results["_trades"])

# graph
tema_values = results._strategy.tema_values
tema_values = tema_values[-len(data):]
tema_df = pd.DataFrame({'Date': data.index[-len(tema_values):], 'TEMA': tema_values})
tema_df.set_index('Date', inplace=True)

combined_df = pd.concat([data['Open'][-len(tema_values):], data['High'][-len(tema_values):],
                         data['Low'][-len(tema_values):], data['Close'][-len(tema_values):], tema_df], axis=1)

mpl_style = mpf.make_mpf_style(base_mpf_style='classic', rc={'figure.facecolor': 'white'},
                               marketcolors=mpf.make_marketcolors(up='g', down='r'))

mpf.plot(combined_df, type='candle', style=mpl_style, title='Triple Exponential Moving Average (TEMA) and Closing Price',
         ylabel='Price',
         figscale=1.1,
         addplot=mpf.make_addplot(tema_df['TEMA'], color='red'), scale_width_adjustment=dict(lines=0.1))

plt.show()

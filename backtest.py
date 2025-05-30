import argparse

import backtrader as bt
import yfinance as yf

from utilities import *


class AutoBotStrategy(bt.Strategy):
    params = (
        ("short_window", 50),
        ("long_window", 200),
        ("rsi_period", 14),
        ("rsi_low", 30),
        ("rsi_high", 70),
    )

    def __init__(self):
        self.dataclose = self.datas[0].close
        self.short_ma = bt.indicators.SimpleMovingAverage(
            self.datas[0], period=self.params.short_window
        )
        self.long_ma = bt.indicators.SimpleMovingAverage(
            self.datas[0], period=self.params.long_window
        )
        self.rsi = bt.indicators.RelativeStrengthIndex(
            self.datas[0], period=self.params.rsi_period
        )

    def next(self):
        if self.short_ma > self.long_ma and self.rsi < self.params.rsi_low:
            if not self.position:
                self.buy()
        elif self.short_ma < self.long_ma and self.rsi > self.params.rsi_high:
            if self.position:
                self.sell()


if __name__ == "__main__":
    cerebro = bt.Cerebro()
    cerebro.addstrategy(AutoBotStrategy)
    config_path = "config/config.yaml"

    parser = argparse.ArgumentParser()
    args = parser.parse_args()

    if args.set:
        args = {v.split("=", 1)[0]: v.split("=", 1)[1] for v in list(args.set)}

    args_group = args["args_group"]

    if args_group.lower() == "robinhood":
        configlists = ["robinhood"]

    elif args_group == "manual_list":
        configlists = ["quantum", "ai", "monitor"]

    if configlists:
        for tickers in configlists:
            group = load_from_config(config_path, tickers)

            for ticker in group:
                # Download historical data
                data = bt.feeds.PandasData(
                    dataname=yf.download(ticker, "2020-01-01", "2021-01-01")
                )

                if data:
                    cerebro.adddata(data)
                    cerebro.broker.set_cash(10000)
                    cerebro.addsizer(bt.sizers.FixedSize, stake=10)
                    cerebro.broker.setcommission(commission=0.001)

                    print("Starting Portfolio Value: %.2f" % cerebro.broker.getvalue())
                    cerebro.run()
                    print("Final Portfolio Value: %.2f" % cerebro.broker.getvalue())

                cerebro.plot()

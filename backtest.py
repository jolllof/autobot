import argparse

import backtrader as bt
import pandas as pd
import yfinance as yf

from utilities import load_from_config


class AutoBotStrategy(bt.Strategy):
    params = (
        ("short_window", 50),
        ("long_window", 200),
        ("rsi_period", 14),
        ("rsi_low", 30),
        ("rsi_high", 70),
    )

    def __init__(self):
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
        if self.short_ma[0] > self.long_ma[0] and self.rsi[0] < self.params.rsi_low:
            if not self.position:
                self.buy()
        elif self.short_ma[0] < self.long_ma[0] and self.rsi[0] > self.params.rsi_high:
            if self.position:
                self.sell()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--set", nargs="+", help="List of key=value pairs for args", required=True
    )
    args = parser.parse_args()

    try:
        args_dict = {v.split("=")[0]: v.split("=")[1] for v in args.set}
    except Exception:
        raise ValueError("Each argument must be in key=value format")

    args_group = args_dict.get("args_group", "").lower()

    if args_group == "robinhood":
        configlists = ["robinhood"]
    elif args_group == "manual_list":
        configlists = ["quantum", "ai", "monitor"]
    else:
        raise ValueError(
            "Invalid or missing 'args_group'. Use 'robinhood' or 'manual_list'"
        )

    cerebro = bt.Cerebro()
    cerebro.addstrategy(AutoBotStrategy)
    cerebro.broker.set_cash(10000)
    cerebro.addsizer(bt.sizers.FixedSize, stake=10)
    cerebro.broker.setcommission(commission=0.001)

    config_path = "config/config.yaml"

    for tickers in configlists:
        group = load_from_config(config_path, tickers)
        for ticker in group:
            print(f"Downloading data for: {ticker}")
            df = yf.download(
                ticker, start="2020-01-01", end="2021-01-01", progress=False
            )
            if isinstance(df, tuple):
                df = df[0]  # Unpack if necessary
            if isinstance(df, pd.DataFrame) and not df.empty:
                df.dropna(inplace=True)
                data = bt.feeds.PandasData(dataname=df)
                cerebro.adddata(data)
            else:
                print(f"Skipping {ticker}, no data returned.")

    print("Starting Portfolio Value: %.2f" % cerebro.broker.getvalue())
    cerebro.run()
    print("Final Portfolio Value: %.2f" % cerebro.broker.getvalue())
    cerebro.plot()

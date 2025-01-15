# TODO: Libraries like backtrader or pyalgotrade for backtesting

from datafetcher import *
import pandas as pd
from utilities import *
import structlog

logger = structlog.get_logger()
calc_config = {
    "rsi_window": 14,
    "atr_window": 14,
    "atr_quantile": 0.75,
    "trend_threshold": 0.1,
    "low_rsi": 30,
    "high_rsi": 70,
    "relative_volume_threshold": 1.5,
}
weakbuy = []
strongbuy = []
weaksell = []
strongsell = []


# Calculate Moving Averages
def get_moving_averages(data, short_window=50, long_window=200):
    result = data.copy()
    result["MA_Short"] = result["Close"].rolling(window=short_window).mean()
    result["MA_Long"] = result["Close"].rolling(window=long_window).mean()
    return result


def avg_is_trending(data):

    trend_threshold = calc_config["trend_threshold"]
    if "MA_Short" not in data or "MA_Long" not in data:
        raise ValueError("Data must contain 'MA_Short' and 'MA_Long' columns.")

    # Calculate the difference as a percentage of the longer moving average
    data["Trend_Strength"] = (data["MA_Short"] - data["MA_Long"]) / data["MA_Long"]

    # Determine if the trend strength exceeds the threshold
    data["Dynamic_Trend_Threshold"] = data["ATR"] * trend_threshold
    data["Is_Trending"] = data["Trend_Strength"].abs() > data["Dynamic_Trend_Threshold"]
    # Determine trend direction (bullish or bearish)
    data["Trend_Direction"] = data["Trend_Strength"].apply(
        lambda x: "Bullish" if x > 0 else "Bearish"
    )

    try:
        # Return the last row's trend status
        return {
            "is_trending": data["Is_Trending"].iloc[-1],
            "trend_direction": data["Trend_Direction"].iloc[-1],
        }
    except IndexError:
        logger.warn(f" avg_is_trending failed: \n{data}")


# Calculate RSI
def get_rsi(data):

    window = calc_config["rsi_window"]
    delta = data["Close"].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
    rs = gain / loss
    data["RSI"] = 100 - (100 / (1 + rs))
    return data


# Calculate Average True Range
def get_atr(data):

    window = calc_config["atr_window"]
    # Calculate True Range (TR)
    high_low = data["High"] - data["Low"]
    high_close = abs(data["High"] - data["Close"].shift(1))
    low_close = abs(data["Low"] - data["Close"].shift(1))

    # Combine into a DataFrame and find the maximum of the three conditions
    true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)

    # Calculate ATR as the moving average of True Range
    data["ATR"] = true_range.rolling(window=window).mean()

    return data


# Volume Based Filter
def volumefilter(data):
    relative_volume_threshold = calc_config["relative_volume_threshold"]
    data["Relative_Volume"] = data["Volume"] / data["Volume"].rolling(window=20).mean()
    data["Volume_Confirmed"] = data["Relative_Volume"] > relative_volume_threshold
    return data


def get_indicators(ticker, start_date, end_date):
    logger.info(f"Getting Indicators for {ticker}")

    stock_data = get_stock_data(ticker, start_date, end_date)
    if not stock_data.empty:
        stock_data = get_moving_averages(stock_data)
        stock_data = get_rsi(stock_data)
        stock_data = get_atr(stock_data)
        stock_data = volumefilter(stock_data)

        return stock_data, ticker
    else:
        return []


def printexecution(plot=False):

    def printloop(category, heading):
        logger.info(heading.upper())
        for stock in category:
            print(stock)
        print("\n")

    if weakbuy:
        printloop(weakbuy, "weakbuy")
    if strongbuy:
        printloop(strongbuy, "strongbuy")
    if weaksell:
        printloop(weaksell, "weaksell")
    if strongsell:
        printloop(strongsell, "strongsell")


def run_analysis(tickers, start_date, end_date, plot=False):
    db = []
    for ticker in tickers:
        try:
            stock_data, ticker = get_indicators(ticker, start_date, end_date)

            # Moving AVG Trend
            avg_trend_stats = avg_is_trending(stock_data)
            avg_trending = avg_trend_stats["is_trending"]
            avg_trend_direction = avg_trend_stats["trend_direction"]

            # RSI
            latest_rsi = stock_data["RSI"].iloc[-1]
            rsi_is_low = latest_rsi < calc_config["low_rsi"]
            rsi_is_high = latest_rsi > calc_config["high_rsi"]

            # ATR
            latest_atr = stock_data["ATR"].iloc[-1]
            atr_quantile = calc_config["atr_quantile"]
            atr_threshold = stock_data["ATR"].quantile(atr_quantile)
            atr_above_threshold = latest_atr > atr_threshold

            # Volume Filter
            latest_volume_confirmed = stock_data["Volume_Confirmed"].iloc[-1]

            # Trade Logic
            if rsi_is_low and avg_trending and avg_trend_direction == "Bullish":
                weakbuy.append[
                    [
                        ticker,
                        stock_data,
                        avg_trending,
                        avg_trend_direction,
                        latest_rsi,
                        latest_atr,
                    ]
                ]
                if atr_above_threshold and latest_volume_confirmed:
                    strongbuy.append[
                        [
                            ticker,
                            stock_data,
                            avg_trending,
                            avg_trend_direction,
                            latest_rsi,
                            latest_atr,
                        ]
                    ]
                    plot_indicators(stock_data, ticker)

            elif rsi_is_high and avg_trending and avg_trend_direction == "Bearish":
                weaksell.append[
                    [
                        ticker,
                        stock_data,
                        avg_trending,
                        avg_trend_direction,
                        latest_rsi,
                        latest_atr,
                    ]
                ]
                if atr_above_threshold and latest_volume_confirmed:
                    strongsell.append[
                        [
                            ticker,
                            stock_data,
                            avg_trending,
                            avg_trend_direction,
                            latest_rsi,
                            latest_atr,
                        ]
                    ]
                    plot_indicators(stock_data, ticker)
            else:
                logger.info(
                    f"Skipping {ticker}: Trending Moving AVG:{avg_trending} ({avg_trend_direction}), RSI:{latest_rsi:.2f}, ATR:{latest_atr:.2f}/{atr_threshold:.2f}, Volume:{latest_volume_confirmed}\n"
                )
                # plot_indicators(stock_data, ticker)
        except Exception as e:
            logger.warn(f"{ticker} completely failed. skipping {e}")
        db.append(stock_data)

    printexecution(plot)
    return db

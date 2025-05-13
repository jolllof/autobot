# TODO: Libraries like backtrader or pyalgotrade for backtesting
# TODO: add logic for mean reversion strategy

import pandas as pd
import structlog
import sys

from datafetcher import *
from utilities import *

logger = structlog.get_logger()

# old_calc_config = {
#     "rsi_window": 14,
#     "atr_window": 14,
#     "adx_window": 14,
#     "atr_quantile": 0.75,
#     "trend_threshold": 0.1,
#     "low_rsi": 30,
#     "high_rsi": 70,
#     "strong_adx": 25,
#     "weak_adx": 20,
#     "relative_volume_threshold": 1.5,
# }


calc_config = {
    "rsi_window": 10,
    "atr_window": 7,
    "adx_window": 10,
    "atr_quantile": 0.65,
    "trend_threshold": 0.05,
    "low_rsi": 40,
    "high_rsi": 60,
    "strong_adx": 20,
    "weak_adx": 15,
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
            "trend_strength_mean": data["Trend_Strength"].abs().mean() > trend_threshold
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

#Average Directional Index
def get_adx(data):

    window = calc_config["adx_window"]
    high = data["High"]
    low = data["Low"]
    close = data["Close"]

    # Calculate +DM and -DM
    plus_dm = high.diff().clip(lower=0)
    minus_dm = (-low.diff()).clip(lower=0)

    # Eliminate crossovers
    plus_dm[plus_dm < minus_dm] = 0
    minus_dm[minus_dm < plus_dm] = 0

    # Calculate True Range (TR)
    tr1 = high - low
    tr2 = abs(high - close.shift(1))
    tr3 = abs(low - close.shift(1))
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)

    # Smooth the components using an exponential moving average
    atr = tr.rolling(window=window).mean()
    smoothed_plus_dm = plus_dm.rolling(window=window).mean()
    smoothed_minus_dm = minus_dm.rolling(window=window).mean()

    # Calculate +DI and -DI
    plus_di = 100 * smoothed_plus_dm / atr
    minus_di = 100 * smoothed_minus_dm / atr

    # Calculate DX (Directional Index)
    dx = 100 * abs(plus_di - minus_di) / (plus_di + minus_di)

    # Calculate ADX (Average Directional Index)
    adx = dx.rolling(window=window).mean()

    # Add results to the DataFrame
    data["+DI"] = plus_di.iloc[-1]
    data["-DI"] = minus_di.iloc[-1]
    data["ADX"] = adx.iloc[-1]

    return data

def get_indicators(ticker, start_date, end_date):
    logger.info(f"Getting Indicators for {ticker}")

    stock_data = get_stock_data(ticker, start_date, end_date)
    if isinstance(stock_data, pd.DataFrame) and not stock_data.empty:

        stock_data = get_moving_averages(stock_data)
        stock_data = get_rsi(stock_data)
        stock_data = get_atr(stock_data)
        stock_data = get_adx(stock_data)
        stock_data = volumefilter(stock_data)

        return stock_data, ticker

    else:
        logger.error(f"Stock Data is Empty for {ticker}")
        sys.exit()

def printexecution(plot=False):

    def printloop(category, heading):
        logger.info(heading.upper())
        for stock in category:
            print(stock[0], stock[1].iloc[-1])
            # plot_indicators(stock[1], stock[0])
        print("\n")

    if weakbuy:
        printloop(weakbuy, "weakbuy")

    if strongbuy:
        printloop(strongbuy, "strongbuy")
    if weaksell:
        printloop(weaksell, "weaksell")
    if strongsell:
        printloop(strongsell, "strongsell")

def determine_market_type(data):
    #Determines if market is trending or something else
    data = get_moving_averages(data)
    trendstrengthmean= avg_is_trending(data)['trend_strength_mean']
    if trendstrengthmean:
        return "Trending Market"
    elif data["Close"].squeeze().std() < calc_config["atr_quantile"]:
        logger.info(f"Market Data: {data["Close"].squeeze().std()} < {calc_config["atr_quantile"]}")
        return "Calm Market"
    elif data["Close"].squeeze().std() > calc_config["atr_quantile"]:
        logger.info(f"Market Data: {data["Close"].squeeze().std()} > {calc_config["atr_quantile"]}")
        return "Volatile Market"
    else:
        return "Sideways Market"

def trending_market_strategy(stock_data, ticker):
    
        # Moving AVG Trend
        avg_trend_stats = avg_is_trending(stock_data)
        avg_trending = avg_trend_stats["is_trending"]
        avg_trend_direction = avg_trend_stats["trend_direction"]

        # RSI
        latest_rsi = stock_data["RSI"].iloc[-1]
        rsi_is_low = latest_rsi < calc_config["low_rsi"]
        rsi_is_high = latest_rsi > calc_config["high_rsi"]

        # ATR (tug of war how much the rope goes back and forth)
        latest_atr = stock_data["ATR"].iloc[-1]
        atr_quantile = calc_config["atr_quantile"]
        atr_threshold = stock_data["ATR"].quantile(atr_quantile)
        atr_above_threshold = latest_atr > atr_threshold

        # ADX (tug of war strength pull on both sides)
        latest_adx = stock_data["ADX"].iloc[-1]
        adx_is_strong = latest_adx > calc_config["strong_adx"]
        adx_is_weak = latest_adx < calc_config["weak_adx"]
        latest_plus_di = stock_data["+DI"].iloc[-1]
        latest_minus_di = stock_data["-DI"].iloc[-1]

        # Volume Filter
        latest_volume_confirmed = stock_data["Volume_Confirmed"].iloc[-1]


        if (
            rsi_is_low and avg_trending and avg_trend_direction == "Bullish" and adx_is_strong   
        ):
            weakbuy.append(
                [
                    ticker,
                    stock_data,
                    avg_trending,
                    avg_trend_direction,
                    latest_rsi,
                    latest_atr,
                ]
            )
            if ( 
                atr_above_threshold and latest_volume_confirmed and latest_plus_di > latest_minus_di
            ):
                strongbuy.append(
                    [
                        ticker,
                        stock_data,
                        avg_trending,
                        avg_trend_direction,
                        latest_rsi,
                        latest_atr,
                    ]
                )
                # plot_indicators(stock_data, ticker)

        elif (
            rsi_is_high and avg_trending and avg_trend_direction == "Bearish" and adx_is_strong
            
        ):
            weaksell.append(
                [
                    ticker,
                    stock_data,
                    avg_trending,
                    avg_trend_direction,
                    latest_rsi,
                    latest_atr,
                ]
            )
            if (
                atr_above_threshold and latest_volume_confirmed and latest_minus_di > latest_plus_di
            ):
                strongsell.append(
                    [
                        ticker,
                        stock_data,
                        avg_trending,
                        avg_trend_direction,
                        latest_rsi,
                        latest_atr,
                    ]
                )
                #plot_indicators(stock_data, ticker)
        else:
            logger.info(
                f"Skipping {ticker}: Moving AVG:{avg_trending} ({avg_trend_direction}), RSI:{latest_rsi:.2f}, ATR:{latest_atr:.2f}/{atr_threshold:.2f}, Volume:{latest_volume_confirmed}, ADX Strong:{adx_is_strong}\n"
            )

def mean_reversion_strategy(data, ticker):
    pass

def run_analysis(tickers, start_date, end_date, plot=False):
    for ticker in tickers:
        # try:
        stock_data, ticker = get_indicators(ticker, start_date, end_date)
        market_type=determine_market_type(stock_data)
        logger.info(f"Market Type: {market_type}")

        #plot_indicators(stock_data, ticker)
        trending_market_strategy(stock_data, ticker)
        # if market_type=='Trending Market':
        #     trending_market_strategy(stock_data, ticker)
        # elif market_type=='Sideways Market':
        #     mean_reversion_strategy(stock_data, ticker)
        # elif market_type=='Volatile Market':
        #     pass
        # elif market_type=='Calm Market':
        #     pass

           
        
    printexecution(plot)

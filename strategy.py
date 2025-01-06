#TODO: get_indicators() is passing the same stock data from function to function, review to make sure that previous function is not altering stock data in a way that affects the next
#TODO: review logic for thresholds (ATR and moving AVG)

import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

import structlog
logger = structlog.get_logger()
plot=False

# Fetch historical data for a stock
def get_stock_data(ticker, start_date, end_date):
	stock_data = yf.download(ticker, start=start_date, end=end_date)
	return stock_data

# Calculate Moving Averages
def get_moving_averages(data, short_window=50, long_window=200):
	data['MA_Short'] = data['Close'].rolling(window=short_window).mean()
	data['MA_Long'] = data['Close'].rolling(window=long_window).mean()
	return data

def avg_is_trending(data, threshold=0.01):
	if 'MA_Short' not in data or 'MA_Long' not in data:
		raise ValueError("Data must contain 'MA_Short' and 'MA_Long' columns.")
	
	# Calculate the difference as a percentage of the longer moving average
	data['Trend_Strength'] = (data['MA_Short'] - data['MA_Long']) / data['MA_Long']
	
	# Determine if the trend strength exceeds the threshold
	data['Is_Trending'] = data['Trend_Strength'].abs() > threshold
	
	try:
	# Return the last row's trend status
		return data['Is_Trending'].iloc[-1]
	except IndexError:
		logger.warn(f" avg_is_trending failed: \n{data}")

# Calculate RSI
def get_rsi(data, window=14):
	delta = data['Close'].diff()
	gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
	loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
	rs = gain / loss
	data['RSI'] = 100 - (100 / (1 + rs))
	return data

# Calculate Average True Range
def get_atr(data, window=14):
	# Calculate True Range (TR)
	high_low = data['High'] - data['Low']
	high_close = abs(data['High'] - data['Close'].shift(1))
	low_close = abs(data['Low'] - data['Close'].shift(1))
	
	# Combine into a DataFrame and find the maximum of the three conditions
	true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
	
	# Calculate ATR as the moving average of True Range
	data['ATR'] = true_range.rolling(window=window).mean()
	
	return data

# Plot stock data with indicators
def plot_indicators(data, ticker):
	plt.figure(figsize=(14, 9))
	
	# Plot Close Price and Moving Averages
	plt.subplot(2, 1, 1)
	plt.plot(data['Close'], label='Close Price', color='black', linewidth=1.2)
	plt.plot(data['MA_Short'], label='20-Day MA', color='blue', linestyle='--')
	plt.plot(data['MA_Long'], label='50-Day MA', color='orange', linestyle='--')
	plt.title(f'{ticker} Stock Price with Moving Averages')
	plt.legend()
	
	# Plot RSI
	plt.subplot(2, 1, 2)
	plt.plot(data['RSI'], label='RSI', color='purple')
	plt.axhline(70, color='red', linestyle='--', linewidth=0.7)
	plt.axhline(30, color='green', linestyle='--', linewidth=0.7)
	plt.title('Relative Strength Index (RSI)')
	plt.legend()
	plt.tight_layout()
	plt.show()

def get_indicators(ticker, start_date, end_date):
	logger.info(f"Getting Indicators for {ticker}")
	
	stock_data = get_stock_data(ticker, start_date, end_date)
	if not stock_data.empty:
		stock_data = get_moving_averages(stock_data)
		stock_data = get_rsi(stock_data)
		stock_data = get_atr(stock_data) 
		
		return stock_data, ticker
	else:
		return []

def run_analysis(tickers, start_date, end_date):
	low_rsi=[]
	high_rsi=[]

	for ticker in tickers:
		try:
			stock_data, ticker=get_indicators(ticker, start_date, end_date)
			
			trend_status = avg_is_trending(stock_data)

			latest_rsi = stock_data['RSI'].iloc[-1]
			rsi_is_low = latest_rsi < 30
			rsi_is_high = latest_rsi > 70

			latest_atr=stock_data['ATR'].iloc[-1]
			atr_threshold = stock_data['ATR'].mean() * 1.5
			atr_above_threshold=latest_atr > atr_threshold

			if rsi_is_low and trend_status and atr_above_threshold:
				low_rsi.append(ticker)
				if plot:
					plot_indicators(stock_data, ticker)
			elif rsi_is_high and trend_status and atr_above_threshold:
				high_rsi.append(ticker)
				if plot:
					plot_indicators(stock_data, ticker)
			else:
				logger.info(f"Skipping {ticker}: Trending Moving AVG:{trend_status}, RSI:{latest_rsi:.2f}, ATR:{latest_atr:.2f}/{atr_threshold:.2f}\n")
		except ValueError:
			logger.warn(f'{ticker} completely failed. skipping')

	logger.info(f"High RSI: {' '.join(high_rsi)} \nLow RSI: {' '.join(low_rsi)}")
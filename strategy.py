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
def calculate_moving_averages(data, short_window=50, long_window=200):
	data['MA_Short'] = data['Close'].rolling(window=short_window).mean()
	data['MA_Long'] = data['Close'].rolling(window=long_window).mean()
	return data

# Calculate RSI
def calculate_rsi(data, window=14):
	delta = data['Close'].diff()
	gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
	loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
	rs = gain / loss
	data['RSI'] = 100 - (100 / (1 + rs))
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

# Run Moving AVG, ADX, ATR, RSI and Volume Based Filter
def get_indicators(ticker, start_date, end_date):
	logger.info(f"Getting RSI and Moving AVG for {ticker}")
	
	stock_data = get_stock_data(ticker, start_date, end_date)
	stock_data = calculate_moving_averages(stock_data)
	stock_data = calculate_rsi(stock_data)
	
	return stock_data, ticker

def run_analysis(tickers, start_date, end_date):
	low_rsi=[]
	high_rsi=[]

	for ticker in tickers:
		stock_data, ticker=get_indicators(ticker, start_date, end_date)
		latest_rsi = stock_data['RSI'].iloc[-1]

		if latest_rsi < 30:
			low_rsi.append(ticker)
			if plot:
				plot_indicators(stock_data, ticker)
		elif latest_rsi > 70:
			high_rsi.append(ticker)
			if plot:
				plot_indicators(stock_data, ticker)
		else:
			logger.info(f"Skipping {ticker}: RSI is within normal range ({latest_rsi:.2f})")

	logger.info(f"\nHigh RSI: {' '.join(high_rsi)} \nLow RSI: {' '.join(low_rsi)}")



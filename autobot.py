import os
import yaml
from rsi_movingavg import *
import structlog
from datetime import datetime, timedelta

logger = structlog.get_logger()
os.system('clear')

def load_tickers_from_config(config_path):
	with open(config_path, 'r') as file:
		config = yaml.safe_load(file)
		return config.get('tickers', [])

def get_rsi_and_movingavgs(ticker, start_date, end_date):
	logger.info(f"Getting RSI and Moving AVG for {ticker}")
	
	stock_data = get_stock_data(ticker, start_date, end_date)
	stock_data = calculate_moving_averages(stock_data)
	stock_data = calculate_rsi(stock_data)
	latest_rsi = stock_data['RSI'].iloc[-1]
	if latest_rsi < 30 or latest_rsi > 70:
		plot_indicators(stock_data, ticker)
	else:
		logger.info(f"Skipping {ticker}: RSI is within normal range ({latest_rsi:.2f})")

def main():
	logger.info('Initiating Autobot')
	end_date = datetime.today().date()
	start_date = datetime.today().date() - timedelta(days=730)
	logger.info(f'Date Range: {start_date} - {end_date}')

	config_path = 'config.yaml'
	tickers=load_tickers_from_config(config_path)
	for ticker in tickers:
		get_rsi_and_movingavgs(ticker, start_date, end_date)

if __name__ == "__main__":
	main()
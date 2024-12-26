#TODO: line 49 split message between low RSI and high RSI

import os
import yaml
from rsi_movingavg import *
from textbot import send_sms_via_email
import structlog
from datetime import datetime, timedelta

logger = structlog.get_logger()
os.system('clear')
plot=False

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

	if latest_rsi < 30:
		return ticker,'low_rsi'
		if plot:
			plot_indicators(stock_data, ticker)
	elif latest_rsi > 70:
		return ticker, 'high_rsi'
		if plot:
			plot_indicators(stock_data, ticker)
	else:
		logger.info(f"Skipping {ticker}: RSI is within normal range ({latest_rsi:.2f})")
		return None, None
def main():
	logger.info('Initiating Autobot')
	low_rsi=[]
	high_rsi=[]

	end_date = datetime.today().date()
	start_date = datetime.today().date() - timedelta(days=730)
	logger.info(f'Date Range: {start_date} - {end_date}')

	config_path = 'config.yaml'
	tickers=load_tickers_from_config(config_path)
	for ticker in tickers:
		ticker, rsi=get_rsi_and_movingavgs(ticker, start_date, end_date)
		if rsi == 'high_rsi':
			high_rsi.append(ticker)
		elif rsi == 'low_rsi':
			low_rsi.append(ticker)
	
	logger.info(f"High RSI: {' '.join(high_rsi)} \nLow RSI: {' '.join(low_rsi)}")
	
	#txt='RSI movers: '+' '.join(rsi_tickers)
	#print(txt)
	
	

	
	# text_message=f""
	# send_sms_via_email(text_message)


if __name__ == "__main__":
	main()
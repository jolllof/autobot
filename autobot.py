import os
from strategy import *
from utilities import *
from textbot import send_sms_via_email
from finnhub import *
import structlog
from datetime import datetime, timedelta

logger = structlog.get_logger()
os.system('clear')

def main():
	logger.info('Initiating Autobot')

	end_date = datetime.today().date()
	start_date = datetime.today().date() - timedelta(days=730)
	logger.info(f'Date Range: {start_date} - {end_date}')

	#Configuration
	config_path = 'config.yaml'
	tickers=load_from_config(config_path, 'robinhood_tickers')
	finnhub_creds=load_from_config(config_path,'finnhub')
	stock_categories=load_from_config(config_path,'stock_categories')

	finnhub_base_url=finnhub_creds['base_url']
	finnhub_api_key=os.getenv(finnhub_creds['api_key'])
	
	#FinnHub Stock Categories
	symbols=get_all_stocks(finnhub_api_key, finnhub_base_url)
	matches=get_stock_groups(symbols, stock_categories)

	x=input(matches)

	#Run Moving AVG, ADX, ATR, RSI and Volume Based Filter
	run_analysis(tickers, start_date, end_date)


	#txt='RSI movers: '+' '.join(rsi_tickers)
	#print(txt)

	# text_message=f""
	# send_sms_via_email(text_message)


if __name__ == "__main__":
	main()
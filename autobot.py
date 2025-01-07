#TODO: finnhub basic financials could provide more details for stock's performance
#TODO: track price changes likely in plots
#TODO: add ADX calculations


import os
from strategy import *
from utilities import *
from textbot import send_sms_via_email
from datafetcher import *
import structlog
from datetime import datetime, timedelta

logger = structlog.get_logger()
os.system('clear')

def main():
	logger.info('Initiating Autobot')

	#Configuration
	end_date = datetime.today().date()
	start_date = datetime.today().date() - timedelta(days=730)
	logger.info(f'Date Range: {start_date} - {end_date}')
	config_path = 'config.yaml'

	#Robinhood
	robinhoodstocks=load_from_config(config_path, 'robinhood_tickers')
	fourstopstocks=load_from_config(config_path, 'fourstopstocks')

	#FINNHUB Categorial Stock Search
	stock_categories=load_from_config(config_path,'stock_categories')
	finnhub_creds=load_from_config(config_path,'finnhub')
	finnhub_base_url=finnhub_creds['base_url']
	finnhub_api_key=os.getenv(finnhub_creds['api_key'])
	symbols=get_all_stocks(finnhub_api_key, finnhub_base_url)
	matches=get_stock_groups(symbols, stock_categories)
	categoricalstocks=list(matches.keys())
	

	#YAHOO Finance Trending
	yahoo_finance_urls=load_from_config(config_path, 'yahoo_finance')
	yahoo_trending_url=yahoo_finance_urls['trending_url']
	trending_tickers = fetch_trending_tickers(yahoo_trending_url)
	trendingstocks=trending_tickers['symbol'].tolist()


	#Run Moving AVG, ADX, ATR, RSI and Volume Based Filter
	#run_analysis(trendingstocks, start_date, end_date)
	#run_analysis(categoricalstocks, start_date, end_date)
	run_analysis(robinhoodstocks, start_date, end_date, plot=True)
	#run_analysis(fourstopstocks, start_date, end_date, plot=True)




	# send_sms_via_email(text_message)


if __name__ == "__main__":
	main()
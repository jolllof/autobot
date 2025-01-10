import requests
from utilities import *
import yfinance as yf
from bs4 import BeautifulSoup
import json
import pandas as pd

#FINNHUB
def get_all_stocks(api_key, base_url):
	# Get all stock symbols available
	stock_symbols_url = f"{base_url}/stock/symbol?exchange=US&token={api_key}"
	results = get_data(stock_symbols_url)
	return results.json()

def get_stock_groups(symbols, keywords):
	# Filter for e.g. tech and AI-related stocks, limiting to US companies
	matched_stocks = {}
	for symbol in symbols:
		description = symbol.get("description", "").lower()
		exchange = symbol.get("exchange", "").upper()

		#if exchange in {"US", "NASDAQ", "NYSE"}:  # Filter for US exchanges
		if any(keyword.lower() in description for keyword in keywords):
			matched_stocks[symbol['symbol']] = symbol['description']

	return matched_stocks


#YAHOO FINANCE
def get_stock_data(ticker, start_date, end_date):
	# Fetch historical data for a stock
	stock_data = yf.download(ticker, start=start_date, end=end_date)
	return stock_data

def fetch_trending_tickers(url):
	#Yahoo Finance Trending Tickers
	headers = {
		"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
	}
	response = requests.get(url, headers=headers)

	# Parse HTML
	soup = BeautifulSoup(response.text, "html.parser")
	script_tag = soup.find("script", {"id": "fin-trending-tickers", "type": "application/json"})
	json_content = json.loads(script_tag.string)
	flatjsoncontent=parse_collections(json_content)
	trending_df=pd.DataFrame(flatjsoncontent)

	return trending_df

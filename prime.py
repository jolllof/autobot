# TODO: automate runs
# TODO: define a proper output notification (email/txt for now)
# TODO: Identify if market is trending at all or something else (mean reversion)
# TODO: add mean-reversion
# TODO: https://trendspider.com/markets/congress-trading/
# TODO: finnhub basic financials could provide more details for stock's performance
# TODO: DevOps stuff: pre-config clean up, github actions

"""Autobot evaulates trending market to find stocks based on:
	Run Moving AVG, ADX, ATR, RSI and Volume Based Filter and recommends buy and sell"""

import os
from datetime import datetime, timedelta

import structlog

from database import *
from datafetcher import *
from strategy import *
from textbot import send_sms_via_email
from utilities import *

logger = structlog.get_logger()
os.system("clear")


def main():
    logger.info("Initiating Autobot")

    # Configuration
    end_date = datetime.today().date()
    start_date = datetime.today().date() - timedelta(days=730)
    config_path = "config/config.yaml"

    # MANUAL LIST
    # configlists = ["robinhood", "quantum", "ai", "monitor"]
    # for tickers in configlists:
    #     logger.info(
    #         f"Analyzing: {tickers.upper()} Stocks For: {start_date} - {end_date}"
    #     )
    #     group = load_from_config(config_path, tickers)
    #     db = run_analysis(group, start_date, end_date, plot=False)
    #     process_data_files(tickers, end_date, db)

    # FINNHUB Categorial Stock Search
    stock_categories = load_from_config(config_path, "stock_categories")
    finnhub_creds = load_from_config(config_path, "finnhub")
    finnhub_base_url = finnhub_creds["base_url"]
    finnhub_api_key = os.getenv(finnhub_creds["api_key"])
    print(finnhub_api_key)

    symbols = get_all_stocks(finnhub_api_key, finnhub_base_url)
    matches = get_stock_groups(symbols, stock_categories)
    categoricalstocks = list(matches.keys())
    run_analysis(categoricalstocks, start_date, end_date)

    # #YAHOO Finance Trending
    # yahoo_finance_urls=load_from_config(config_path, 'yahoo_finance')
    # yahoo_trending_url=yahoo_finance_urls['trending_url']
    # trending_tickers = fetch_trending_tickers(yahoo_trending_url)
    # trendingstocks=trending_tickers['symbol'].tolist()
    # run_analysis(trendingstocks, start_date, end_date)

    # send_sms_via_email(text_message)


if __name__ == "__main__":
    main()

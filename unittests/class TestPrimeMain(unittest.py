import unittest
from unittest.mock import MagicMock, patch

from prime import main


class TestPrimeMain(unittest.TestCase):

    @patch("prime.load_from_config")
    @patch("prime.run_analysis")
    def test_main_robinhood(self, mock_run_analysis, mock_load_from_config):
        args = {"args_group": "robinhood"}
        mock_load_from_config.return_value = MagicMock()
        main(args)
        mock_load_from_config.assert_called_once_with("config/config.yaml", "robinhood")
        mock_run_analysis.assert_called()

    @patch("prime.load_from_config")
    @patch("prime.run_analysis")
    def test_main_manual_list(self, mock_run_analysis, mock_load_from_config):
        args = {"args_group": "manual_list"}
        mock_load_from_config.return_value = MagicMock()
        main(args)
        mock_load_from_config.assert_any_call("config/config.yaml", "quantum")
        mock_load_from_config.assert_any_call("config/config.yaml", "ai")
        mock_load_from_config.assert_any_call("config/config.yaml", "monitor")
        mock_run_analysis.assert_called()

    @patch("prime.load_from_config")
    @patch("prime.fetch_trending_tickers")
    @patch("prime.run_analysis")
    def test_main_trending(
        self, mock_run_analysis, mock_fetch_trending_tickers, mock_load_from_config
    ):
        args = {"args_group": "trending"}
        mock_load_from_config.return_value = {"trending_url": "mock_url"}
        mock_fetch_trending_tickers.return_value = {"symbol": ["AAPL", "GOOGL"]}
        main(args)
        mock_load_from_config.assert_called_once_with(
            "config/config.yaml", "yahoo_finance"
        )
        mock_fetch_trending_tickers.assert_called_once_with("mock_url")
        mock_run_analysis.assert_called()

    @patch("prime.load_from_config")
    @patch("prime.get_all_stocks")
    @patch("prime.get_stock_groups")
    @patch("prime.run_analysis")
    def test_main_categorical(
        self,
        mock_run_analysis,
        mock_get_stock_groups,
        mock_get_all_stocks,
        mock_load_from_config,
    ):
        args = {"args_group": "categorical"}
        mock_load_from_config.side_effect = [
            {"category1": "mock_category"},
            {"base_url": "mock_base_url", "api_key": "mock_api_key"},
        ]
        mock_get_all_stocks.return_value = ["AAPL", "GOOGL"]
        mock_get_stock_groups.return_value = {"AAPL": "category1"}
        main(args)
        mock_load_from_config.assert_any_call("config/config.yaml", "stock_categories")
        mock_load_from_config.assert_any_call("config/config.yaml", "finnhub")
        mock_get_all_stocks.assert_called_once_with("mock_api_key", "mock_base_url")
        mock_get_stock_groups.assert_called_once_with(
            ["AAPL", "GOOGL"], {"category1": "mock_category"}
        )
        mock_run_analysis.assert_called()

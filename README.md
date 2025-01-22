# Autobot (Trend-Following) Trading Bot

![Auto Trading Bot Logo](https://raw.githubusercontent.com/jolllof/autobot/refs/heads/main/autobot.webp)
## Overview
The Autobot Trading Bot is designed to capitalize on market trends by employing technical analysis indicators. The bot is optimized for trading cryptocurrencies, AI stocks, and tech stocks, and operates using a combination of trend confirmation and volatility analysis techniques.

This document outlines the bot's functionality, setup, and usage.

---

## Features
### Core Indicators
1. **Moving Averages (MAs):**
   - Uses Exponential Moving Averages (EMA) to identify trends.
   - Significant separation between moving averages (e.g., 20 EMA and 50 EMA) indicates a strong trend.

2. **Relative Strength Index (RSI):**
   - RSI > 70 triggers a sell signal.
   - RSI < 30 triggers a buy signal.
   - Signals are used only when confirmed by moving averages.

3. **Average True Range (ATR):**
   - Measures market volatility.
   - High ATR suggests trending potential.
   - Low ATR indicates likely mean-reversion.

4. **Average Directional Index (ADX):**
   - ADX > 25 signals a strong trend.
   - ADX < 20 indicates a weak trend.

5. **Volume-Based Filter:**
   - Confirms breakouts or trend strength.
   - Relative Volume > 1.5 indicates strong market participation.

6. **Average Directional Index:**
   - Strong Directional Index > 25
   - Weak Directional index < 20

### Supported Markets
- Cryptocurrencies (e.g., Bitcoin, Ethereum)
- AI stocks
- Tech stocks

### Strategy
The bot employs a trend-following approach by combining multiple indicators to:
- Detect and confirm trends.
- Filter out false signals.
- Adapt to varying market conditions.

---

## Requirements
- Python 3.11+
- Libraries:
- 'os'
- 'yaml'
- 'structlog'
- 'datetime'
- 'yfinance'
- 'pandas'
- 'numpy'
- 'matplotlib'
- 'smtplib'
- 'requests'
- 'bs4'
- 'json'
---

## Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/username/autobot.git
   cd autobot
   ```

2. Install the dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Configure API keys:
   - Add your exchange API keys to `config.json`.


---

## Usage
1. **Run the bot:**
   ```bash
   Python -m prime --set args_group=<manual_list|trending|categorical>
   ```

2. **Backtesting:**
   - Not functioning at the moment
   - Use historical data to test strategies.
   - Example:
     ```bash
     python backtest.py --symbol BTC/USD --start 2020-01-01 --end 2022-01-01
     ```

3. **Live Trading:**
   - Activate live trading mode by updating the `config.json` file.
   - Monitor trades in real-time through logs or dashboards.

---

## Bot Logic
1. Fetch live or historical data.
2. Compute technical indicators (MAs, RSI, ATR, ADX, Volume).
3. Confirm trends using a multi-indicator approach.
4. Execute trades based on:
   - Buy signals: RSI < 30, strong trend (ADX > 25), high volatility (ATR).
   - Sell signals: RSI > 70, strong trend (ADX > 25), high volatility (ATR).
5. Log trades and monitor performance.

---

## Contribution
1. Fork the repository.
2. Create a feature branch:
   ```bash
   git checkout -b feature-name
   ```
3. Commit changes and create a pull request.

---

## Code Cleanups

Before committing code, ensure the following:

1. Run `pre-commit run --all-files` to apply hooks.

---

## Future Improvements
- Automate stock runs
- Add Mean-Reversion functionality for non-trending markets
- Add DevOps functionalities: pre-config clean up, github actions AWS monitoring
- Database/storage functionalities
- Add Backtesting functionality

---

## License
This project is licensed under the MIT License. See the `LICENSE` file for details.

---

## Support
For questions or issues, feel free to open an issue on GitHub or contact Michael Hammond at jolllofcodes@gmail.com.

---

## Acknowledgments
This bot was developed with a focus on simplicity and robustness, utilizing well-established technical indicators and strategies.

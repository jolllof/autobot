import structlog
import logging
from datetime import datetime

# Setting up logging
logging.basicConfig(
    format="%(message)s",  # Only the structured log output
    level=logging.DEBUG,
)

# Create a structlog processor to format the log output
def add_timestamp(_, __, event_dict):
    """Add timestamp to each log entry."""
    event_dict["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return event_dict

# Set up structlog with the desired processors
log = structlog.get_logger()

# Add processors for structlog formatting
log.configure(
    processors=[
        structlog.processors.KeyValueRenderer(key_order=["timestamp", "event"]),
        add_timestamp,  # Custom processor to add the timestamp
        structlog.processors.JSONRenderer(),  # Optional: for JSON output
    ],
    context_class=dict,
    wrapper_class=structlog.stdlib.BoundLogger,
    logger_factory=structlog.stdlib.get_logger,
)

# Example of structured logging usage
def log_trade_execution(order_type, amount, price, status):
    """Log trade executions with structured data."""
    log.info(
        "Executed trade",
        order_type=order_type,
        amount=amount,
        price=price,
        status=status,
    )

def log_trade_error(error_message):
    """Log errors in trade execution."""
    log.error("Error occurred", error_message=error_message)

def log_strategy_update(strategy_name, parameters):
    """Log updates to trading strategy."""
    log.info(
        "Strategy updated",
        strategy_name=strategy_name,
        parameters=parameters,
    )

def log_risk_management(message):
    """Log risk management events."""
    log.warning("Risk management event", message=message)

def log_backtest_results(strategy_name, performance_metrics):
    """Log backtesting results."""
    log.info(
        "Backtest completed",
        strategy_name=strategy_name,
        performance_metrics=performance_metrics,
    )

# Example usage of structured logging
if __name__ == "__main__":
    log_trade_execution("buy", 100, 45.67, "successful")
    log_trade_error("Insufficient funds for trade")
    log_strategy_update("MACD Strategy", {"fast_length": 12, "slow_length": 26, "signal_length": 9})
    log_risk_management("Stop loss triggered for BTC position")
    log_backtest_results("RSI Strategy", {"sharpe_ratio": 1.5, "max_drawdown": -10.2})

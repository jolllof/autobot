import structlog
from colorama import Fore, Style

# Configure structlog
structlog.configure(
    processors=[
        structlog.processors.KeyValueRenderer(key_order=["event"]),  # Optional: Ensures "event" is first
    ],
    context_class=dict,
    wrapper_class=structlog.make_filtering_bound_logger(10),
    logger_factory=structlog.PrintLoggerFactory(),
    cache_logger_on_first_use=True,
)

# Initialize logger
logger = structlog.get_logger()

# Example usage with colorized log message
ticker = "RGTI"
avg_trending = True
avg_trend_direction = "Bullish"
latest_rsi = 48.23
latest_atr = 3.75
atr_threshold = 0.21
latest_volume_confirmed = True

logger.info(
    f"Skipping {Fore.CYAN}{ticker}{Style.RESET_ALL}: "
    f"Trending Moving AVG:{Fore.GREEN if avg_trending else Fore.RED}{avg_trending}{Style.RESET_ALL} "
    f"({Fore.YELLOW}{avg_trend_direction}{Style.RESET_ALL}), "
    f"RSI:{Fore.MAGENTA}{latest_rsi:.2f}{Style.RESET_ALL}, "
    f"ATR:{Fore.BLUE}{latest_atr:.2f}/{atr_threshold:.2f}{Style.RESET_ALL}, "
    f"Volume:{Fore.GREEN if latest_volume_confirmed else Fore.RED}{latest_volume_confirmed}{Style.RESET_ALL}"
)

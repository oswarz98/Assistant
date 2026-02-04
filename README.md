# MarketScope

MarketScope is a desktop market analysis application for Stocks, Crypto, and Forex. It provides informational analysis only (no trade execution) with trend bias, key levels, confidence scoring, and idea generation.

## Features
- Multi-market support (stocks, crypto, forex)
- Trend and momentum summary across timeframes
- Support/resistance detection
- Indicator suite (RSI, MACD, EMA, ATR, VWAP)
- Confidence score with transparent scoring breakdown
- Top 5 scanners for intraday and swing ideas
- Demo mode with public endpoints and sample data fallback

## Setup
1. Install Python 3.11+
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the app:
   ```bash
   python main.py
   ```

## Data providers
MarketScope uses a pluggable data-client architecture. The default `DemoDataClient` provides sample data and can optionally use public endpoints. To add a new data source:
1. Create a new client in `data/` that implements `MarketDataClient`.
2. Register it in `data/client_factory.py`.
3. Expose any optional API keys in Settings.

## Disclaimer
MarketScope provides informational analysis only. It does not execute trades or provide financial guarantees.

# OddScope

OddScope is a desktop sports betting market analysis app. It provides **informational analysis only** and does **not** place bets or automate wagering. The app focuses on transparent probability modeling, confidence scoring, and clear explanations for the most probable outcomes.

## Features
- Game & Market Explorer (Moneyline, Spread, Totals)
- Odds comparison across sportsbooks with implied probability + best price highlight
- Explainable “most probable outcome” engine with confidence scoring
- Top 5 most confident picks + Top 5 best value picks
- Simplistic vs Pro modes
- Odds movement + probability charts (pyqtgraph)
- Demo mode with sample JSON data
- SQLite caching for games, odds snapshots, and user settings

## Supported sports (MVP)
- NBA
- NHL

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

## Demo mode
OddScope ships with sample data in `data/oddscope_demo.json`. This demo mode is the default so the app can run without API keys.

## Provider architecture
OddScope uses a provider abstraction layer so you can swap data sources.

1. Implement a sports stats provider in `data_providers/base.py` (`SportsDataProvider`).
2. Implement an odds provider in `data_providers/base.py` (`OddsDataProvider`).
3. Register both in `data_providers/registry.py` by returning a `ProviderBundle`.

## Adding new leagues or books
1. Add the league enum in `models/types.py`.
2. Update providers to map API responses into `Game` and `MarketSnapshot`.
3. Extend demo data (optional) with the new league and odds markets.

## Disclaimer
OddScope provides informational analysis only. No guaranteed outcomes. OddScope does **not** place bets. Bet responsibly.

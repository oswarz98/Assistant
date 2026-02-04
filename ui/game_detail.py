from __future__ import annotations

from typing import List

import pyqtgraph as pg
from PySide6.QtWidgets import (
    QComboBox,
    QLabel,
    QHBoxLayout,
    QListWidget,
    QTableWidget,
    QTableWidgetItem,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from engine.odds import implied_probability_from_american
from models.types import Game, GameAnalysis, League, MarketSnapshot, MarketType


class GameDetailView(QWidget):
    def __init__(self) -> None:
        super().__init__()
        layout = QVBoxLayout(self)
        header = QHBoxLayout()
        self.league_picker = QComboBox()
        for league in League:
            self.league_picker.addItem(league.value, league)
        self.game_picker = QComboBox()
        self.market_picker = QComboBox()
        for market in MarketType:
            self.market_picker.addItem(market.value, market)

        header.addWidget(QLabel("League"))
        header.addWidget(self.league_picker)
        header.addWidget(QLabel("Game"))
        header.addWidget(self.game_picker)
        header.addWidget(QLabel("Market"))
        header.addWidget(self.market_picker)
        layout.addLayout(header)

        self.tabs = QTabWidget()
        self.simple_tab = QWidget()
        self.pro_tab = QWidget()
        self.tabs.addTab(self.simple_tab, "Simplistic")
        self.tabs.addTab(self.pro_tab, "Pro")
        layout.addWidget(self.tabs)

        self._build_simple_tab()
        self._build_pro_tab()

    def _build_simple_tab(self) -> None:
        layout = QVBoxLayout(self.simple_tab)
        self.pick_label = QLabel("Pick: --")
        self.confidence_label = QLabel("Confidence: --")
        self.model_prob_label = QLabel("Model Probability: --")
        self.ev_label = QLabel("Expected Value: --")
        info = QHBoxLayout()
        info.addWidget(self.pick_label)
        info.addWidget(self.confidence_label)
        info.addWidget(self.model_prob_label)
        info.addWidget(self.ev_label)
        layout.addLayout(info)

        self.odds_table = QTableWidget(0, 5)
        self.odds_table.setHorizontalHeaderLabels(["Book", "Home", "Away", "Line", "Implied Prob"])
        layout.addWidget(self.odds_table)

        self.why_list = QListWidget()
        layout.addWidget(QLabel("Why this lean"))
        layout.addWidget(self.why_list)

    def _build_pro_tab(self) -> None:
        layout = QHBoxLayout(self.pro_tab)

        left = QVBoxLayout()
        self.breakdown_table = QTableWidget(0, 2)
        self.breakdown_table.setHorizontalHeaderLabels(["Driver", "Score"])
        self.top_drivers = QLabel("Top drivers: --")
        left.addWidget(QLabel("Confidence breakdown"))
        left.addWidget(self.breakdown_table)
        left.addWidget(self.top_drivers)

        self.risk_list = QListWidget()
        left.addWidget(QLabel("Risk flags"))
        left.addWidget(self.risk_list)

        right = QVBoxLayout()
        self.odds_chart = pg.PlotWidget(background="#0f1216")
        self.odds_chart.showGrid(x=True, y=True, alpha=0.3)
        self.prob_chart = pg.PlotWidget(background="#0f1216")
        self.prob_chart.showGrid(x=True, y=True, alpha=0.3)
        right.addWidget(QLabel("Line movement"))
        right.addWidget(self.odds_chart, stretch=2)
        right.addWidget(QLabel("Projected probability distribution"))
        right.addWidget(self.prob_chart, stretch=1)

        layout.addLayout(left, stretch=2)
        layout.addLayout(right, stretch=3)

    def update_games(self, games: List[Game]) -> None:
        self.game_picker.clear()
        for game in games:
            label = f"{game.away_team} @ {game.home_team}"
            self.game_picker.addItem(label, game.id)

    def update_analysis(self, analysis: GameAnalysis | None, snapshots: List[MarketSnapshot]) -> None:
        if not analysis:
            return
        market = self.market_picker.currentData() or MarketType.MONEYLINE
        recommendation = analysis.recommendations.get(market)
        if not recommendation:
            return

        self.pick_label.setText(f"Pick: {recommendation.pick}")
        self.confidence_label.setText(f"Confidence: {recommendation.confidence:.0f}%")
        self.model_prob_label.setText(f"Model Probability: {recommendation.model_probability * 100:.0f}%")
        self.ev_label.setText(f"Expected Value: {recommendation.expected_value:.2f}")

        self._update_odds_table(snapshots, analysis.game.id, market)
        self._update_why(recommendation.why)
        self._update_breakdown(recommendation)
        self._update_risk_flags(recommendation.risk_flags)
        self._plot_odds_movement(snapshots, analysis.game.id, market)
        self._plot_probability_distribution(recommendation.model_probability)

    def _update_odds_table(self, snapshots: List[MarketSnapshot], game_id: str, market: MarketType) -> None:
        snapshot = next((snap for snap in snapshots if snap.game_id == game_id and snap.market == market), None)
        if not snapshot:
            return
        self.odds_table.setRowCount(len(snapshot.books))
        for row, book in enumerate(snapshot.books):
            implied = implied_probability_from_american(book.home)
            self.odds_table.setItem(row, 0, QTableWidgetItem(book.book))
            self.odds_table.setItem(row, 1, QTableWidgetItem(str(book.home)))
            self.odds_table.setItem(row, 2, QTableWidgetItem(str(book.away)))
            self.odds_table.setItem(row, 3, QTableWidgetItem(str(book.line or "--")))
            self.odds_table.setItem(row, 4, QTableWidgetItem(f"{implied:.2%}"))
        self.odds_table.resizeColumnsToContents()

    def _update_why(self, reasons: List[str]) -> None:
        self.why_list.clear()
        for reason in reasons:
            self.why_list.addItem(reason)

    def _update_breakdown(self, recommendation) -> None:
        breakdown = recommendation.breakdown
        self.breakdown_table.setRowCount(6)
        self.breakdown_table.clearContents()
        for row, (driver, score) in enumerate(
            [
                ("Team strength differential", breakdown.team_strength),
                ("Recent form & consistency", breakdown.recent_form),
                ("Matchup edges", breakdown.matchup_edges),
                ("Injuries/lineup impact", breakdown.injuries),
                ("Schedule/rest/travel", breakdown.rest_travel),
                ("Market movement/price efficiency", breakdown.market_signal),
            ]
        ):
            self.breakdown_table.setItem(row, 0, QTableWidgetItem(driver))
            self.breakdown_table.setItem(row, 1, QTableWidgetItem(f"{score:.1f}"))
        self.breakdown_table.resizeColumnsToContents()
        self.top_drivers.setText(f"Top drivers: {', '.join(recommendation.top_drivers)}")

    def _update_risk_flags(self, flags: List[str]) -> None:
        self.risk_list.clear()
        for flag in flags:
            self.risk_list.addItem(flag)

    def _plot_odds_movement(self, snapshots: List[MarketSnapshot], game_id: str, market: MarketType) -> None:
        self.odds_chart.clear()
        snapshot = next((snap for snap in snapshots if snap.game_id == game_id and snap.market == market), None)
        if not snapshot or not snapshot.movement:
            return
        x = list(range(len(snapshot.movement)))
        home = [point.home for point in snapshot.movement]
        self.odds_chart.plot(x, home, pen=pg.mkPen(color="#1f6feb", width=2))

    def _plot_probability_distribution(self, probability: float) -> None:
        self.prob_chart.clear()
        values = [max(0.0, min(1.0, probability + (i - 50) * 0.002)) for i in range(100)]
        self.prob_chart.plot(values, pen=pg.mkPen(color="#22c55e", width=2))

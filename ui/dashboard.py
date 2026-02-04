from __future__ import annotations

from typing import List

import pyqtgraph as pg
from PySide6.QtWidgets import QLabel, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget

from models.types import MarketSnapshot, ScannerResult


class DashboardView(QWidget):
    def __init__(self) -> None:
        super().__init__()
        layout = QVBoxLayout(self)
        title = QLabel("OddScope Dashboard")
        title.setStyleSheet("font-size: 22px; font-weight: 700;")
        layout.addWidget(title)

        self.top_confident = QTableWidget(0, 6)
        self.top_confident.setHorizontalHeaderLabels(
            ["Matchup", "League", "Market", "Pick", "Confidence", "Best Book"]
        )
        layout.addWidget(QLabel("Top 5 most confident picks"))
        layout.addWidget(self.top_confident)

        self.top_value = QTableWidget(0, 6)
        self.top_value.setHorizontalHeaderLabels(
            ["Matchup", "League", "Market", "Pick", "Edge %", "Best Book"]
        )
        layout.addWidget(QLabel("Top 5 best value picks"))
        layout.addWidget(self.top_value)

        self.movement_chart = pg.PlotWidget(background="#0f1216")
        self.movement_chart.showGrid(x=True, y=True, alpha=0.3)
        layout.addWidget(QLabel("Trending line movement"))
        layout.addWidget(self.movement_chart, stretch=1)

    def update_tables(self, confident: List[ScannerResult], value: List[ScannerResult]) -> None:
        self._populate_confident(confident)
        self._populate_value(value)

    def update_movement_chart(self, snapshots: List[MarketSnapshot]) -> None:
        self.movement_chart.clear()
        if not snapshots:
            return
        movement = snapshots[0].movement
        if not movement:
            return
        x = list(range(len(movement)))
        y = [point.home for point in movement]
        self.movement_chart.plot(x, y, pen=pg.mkPen(color="#f97316", width=2))

    def _populate_confident(self, results: List[ScannerResult]) -> None:
        self.top_confident.setRowCount(len(results))
        for row, result in enumerate(results):
            self.top_confident.setItem(row, 0, QTableWidgetItem(result.matchup))
            self.top_confident.setItem(row, 1, QTableWidgetItem(result.league.value))
            self.top_confident.setItem(row, 2, QTableWidgetItem(result.market.value))
            self.top_confident.setItem(row, 3, QTableWidgetItem(result.pick))
            self.top_confident.setItem(row, 4, QTableWidgetItem(f"{result.confidence:.0f}%"))
            self.top_confident.setItem(row, 5, QTableWidgetItem(result.best_book))
        self.top_confident.resizeColumnsToContents()

    def _populate_value(self, results: List[ScannerResult]) -> None:
        self.top_value.setRowCount(len(results))
        for row, result in enumerate(results):
            self.top_value.setItem(row, 0, QTableWidgetItem(result.matchup))
            self.top_value.setItem(row, 1, QTableWidgetItem(result.league.value))
            self.top_value.setItem(row, 2, QTableWidgetItem(result.market.value))
            self.top_value.setItem(row, 3, QTableWidgetItem(result.pick))
            self.top_value.setItem(row, 4, QTableWidgetItem(f"{result.edge:.1f}%"))
            self.top_value.setItem(row, 5, QTableWidgetItem(result.best_book))
        self.top_value.resizeColumnsToContents()

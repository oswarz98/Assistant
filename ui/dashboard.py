from __future__ import annotations

from typing import List

from PySide6.QtWidgets import QLabel, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget

from models.types import ScannerResult


class DashboardView(QWidget):
    def __init__(self) -> None:
        super().__init__()
        layout = QVBoxLayout(self)
        self.title = QLabel("MarketScope Dashboard")
        self.title.setStyleSheet("font-size: 22px; font-weight: 700;")
        layout.addWidget(self.title)

        self.top_trades = QTableWidget(0, 5)
        self.top_trades.setHorizontalHeaderLabels(["Symbol", "Market", "Confidence", "Expected R", "Summary"])
        layout.addWidget(QLabel("Top 5 Trades to Take Now"))
        layout.addWidget(self.top_trades)

        self.top_holds = QTableWidget(0, 5)
        self.top_holds.setHorizontalHeaderLabels(["Symbol", "Market", "Confidence", "Expected R", "Summary"])
        layout.addWidget(QLabel("Top 5 Holds"))
        layout.addWidget(self.top_holds)

    def update_tables(self, trades: List[ScannerResult], holds: List[ScannerResult]) -> None:
        self._populate(self.top_trades, trades[:5])
        self._populate(self.top_holds, holds[:5])

    def _populate(self, table: QTableWidget, results: List[ScannerResult]) -> None:
        table.setRowCount(len(results))
        for row, result in enumerate(results):
            table.setItem(row, 0, QTableWidgetItem(result.symbol))
            table.setItem(row, 1, QTableWidgetItem(result.market.value))
            table.setItem(row, 2, QTableWidgetItem(f"{result.confidence:.0f}%"))
            table.setItem(row, 3, QTableWidgetItem(f"{result.expected_r:.2f}R"))
            table.setItem(row, 4, QTableWidgetItem(result.summary))
        table.resizeColumnsToContents()

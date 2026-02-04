from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QFormLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QDoubleSpinBox,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from models.types import League, MarketType, ScannerResult


class ScannerView(QWidget):
    def __init__(self) -> None:
        super().__init__()
        layout = QVBoxLayout(self)
        self.filters_form = QFormLayout()

        self.league_picker = QComboBox()
        self.league_picker.addItem("All", None)
        for league in League:
            self.league_picker.addItem(league.value, league)

        self.market_picker = QComboBox()
        self.market_picker.addItem("All", None)
        for market in MarketType:
            self.market_picker.addItem(market.value, market)

        self.min_confidence = QDoubleSpinBox()
        self.min_confidence.setRange(0, 100)
        self.min_confidence.setValue(60)

        self.min_edge = QDoubleSpinBox()
        self.min_edge.setRange(0, 50)
        self.min_edge.setValue(2)

        self.book_list = QListWidget()
        for book in ["DraftKings", "FanDuel", "Pinnacle"]:
            item = QListWidgetItem(book)
            item.setCheckState(Qt.Unchecked)
            self.book_list.addItem(item)

        self.filters_form.addRow("League", self.league_picker)
        self.filters_form.addRow("Market", self.market_picker)
        self.filters_form.addRow("Min Confidence", self.min_confidence)
        self.filters_form.addRow("Min Edge %", self.min_edge)
        self.filters_form.addRow(QLabel("Books"), self.book_list)

        layout.addLayout(self.filters_form)
        self.scan_button = QPushButton("Run Scan")
        layout.addWidget(self.scan_button)

        self.results = QTableWidget(0, 7)
        self.results.setHorizontalHeaderLabels(
            ["Matchup", "League", "Market", "Pick", "Confidence", "Edge %", "Best Book"]
        )
        layout.addWidget(self.results)

    def selected_books(self) -> list[str]:
        books: list[str] = []
        for index in range(self.book_list.count()):
            item = self.book_list.item(index)
            if item.checkState():
                books.append(item.text())
        return books

    def update_results(self, results: list[ScannerResult]) -> None:
        self.results.setRowCount(len(results))
        for row, result in enumerate(results):
            self.results.setItem(row, 0, QTableWidgetItem(result.matchup))
            self.results.setItem(row, 1, QTableWidgetItem(result.league.value))
            self.results.setItem(row, 2, QTableWidgetItem(result.market.value))
            self.results.setItem(row, 3, QTableWidgetItem(result.pick))
            self.results.setItem(row, 4, QTableWidgetItem(f"{result.confidence:.0f}%"))
            self.results.setItem(row, 5, QTableWidgetItem(f"{result.edge:.1f}%"))
            self.results.setItem(row, 6, QTableWidgetItem(result.best_book))
        self.results.resizeColumnsToContents()

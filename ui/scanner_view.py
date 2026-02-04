from __future__ import annotations

from PySide6.QtWidgets import (
    QComboBox,
    QFormLayout,
    QLabel,
    QHBoxLayout,
    QPushButton,
    QSpinBox,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from models.types import MarketType, ScannerResult


class ScannerView(QWidget):
    def __init__(self) -> None:
        super().__init__()
        layout = QVBoxLayout(self)
        self.filters_form = QFormLayout()
        self.market_picker = QComboBox()
        self.market_picker.addItem("All", None)
        for market in MarketType:
            self.market_picker.addItem(market.value, market)
        self.timeframe_picker = QComboBox()
        self.timeframe_picker.addItems(["1m", "5m", "15m", "1h", "4h", "1d"])
        self.min_confidence = QSpinBox()
        self.min_confidence.setRange(0, 100)
        self.min_confidence.setValue(60)
        self.filters_form.addRow("Market", self.market_picker)
        self.filters_form.addRow("Timeframe", self.timeframe_picker)
        self.filters_form.addRow("Min Confidence", self.min_confidence)

        filter_widget = QWidget()
        filter_widget.setLayout(self.filters_form)
        layout.addWidget(filter_widget)

        self.scan_button = QPushButton("Run Scan")
        layout.addWidget(self.scan_button)

        self.results = QTableWidget(0, 5)
        self.results.setHorizontalHeaderLabels(["Symbol", "Market", "Confidence", "Expected R", "Summary"])
        layout.addWidget(self.results)

    def update_results(self, results: list[ScannerResult]) -> None:
        self.results.setRowCount(len(results))
        for row, result in enumerate(results):
            self.results.setItem(row, 0, QTableWidgetItem(result.symbol))
            self.results.setItem(row, 1, QTableWidgetItem(result.market.value))
            self.results.setItem(row, 2, QTableWidgetItem(f"{result.confidence:.0f}%"))
            self.results.setItem(row, 3, QTableWidgetItem(f"{result.expected_r:.2f}R"))
            self.results.setItem(row, 4, QTableWidgetItem(result.summary))
        self.results.resizeColumnsToContents()

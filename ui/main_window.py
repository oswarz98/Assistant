from __future__ import annotations

from typing import List

from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QStackedWidget,
    QWidget,
)

from data.client_factory import build_client
from models.types import MarketType, ScannerFilters
from services.analyzer import MarketAnalyzer
from services.scanner import MarketScanner
from ui.asset_detail import AssetDetailView
from ui.dashboard import DashboardView
from ui.scanner_view import ScannerView
from ui.settings_view import SettingsView


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("MarketScope")
        self.resize(1200, 800)

        container = QWidget()
        layout = QHBoxLayout(container)
        self.sidebar = QListWidget()
        for name in ["Dashboard", "Asset Detail", "Scanner", "Settings"]:
            self.sidebar.addItem(QListWidgetItem(name))
        self.stack = QStackedWidget()
        self.dashboard = DashboardView()
        self.asset_detail = AssetDetailView()
        self.scanner_view = ScannerView()
        self.settings_view = SettingsView()
        self.stack.addWidget(self.dashboard)
        self.stack.addWidget(self.asset_detail)
        self.stack.addWidget(self.scanner_view)
        self.stack.addWidget(self.settings_view)

        layout.addWidget(self.sidebar, stretch=1)
        layout.addWidget(self.stack, stretch=5)
        self.setCentralWidget(container)

        self.client = build_client()
        self.analyzer = MarketAnalyzer(self.client)
        self.scanner = MarketScanner(self.client)

        self.sidebar.currentRowChanged.connect(self.stack.setCurrentIndex)
        self.asset_detail.market_picker.currentIndexChanged.connect(self._update_symbols)
        self.asset_detail.symbol_picker.currentIndexChanged.connect(self._update_analysis)
        self.scanner_view.scan_button.clicked.connect(self._run_scan)

        self.sidebar.setCurrentRow(0)
        self._update_symbols()
        self._refresh_dashboard()

    def _update_symbols(self) -> None:
        market = self.asset_detail.market_picker.currentData()
        market = market or MarketType.STOCKS
        symbols = self.client.list_symbols(market)
        self.asset_detail.update_symbols(symbols)
        if symbols:
            self.asset_detail.symbol_picker.setCurrentIndex(0)

    def _update_analysis(self) -> None:
        symbol = self.asset_detail.symbol_picker.currentText()
        market = self.asset_detail.market_picker.currentData() or MarketType.STOCKS
        if not symbol:
            return
        analysis = self.analyzer.analyze(symbol, market)
        bars = self.client.fetch_bars(symbol, market, "15m", limit=120)
        prices = [bar.close for bar in bars]
        self.asset_detail.update_analysis(analysis, prices)

    def _run_scan(self) -> None:
        market = self.scanner_view.market_picker.currentData()
        filters = ScannerFilters(
            market=market,
            min_confidence=float(self.scanner_view.min_confidence.value()),
            timeframe=self.scanner_view.timeframe_picker.currentText(),
        )
        results = self.scanner.scan(filters)
        self.scanner_view.update_results(results)

    def _refresh_dashboard(self) -> None:
        filters = ScannerFilters(min_confidence=55)
        results = self.scanner.scan(filters)
        self.dashboard.update_tables(results[:5], results[5:10])

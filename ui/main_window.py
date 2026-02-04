from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from data_providers.registry import build_provider_bundle
from models.types import League, ScannerFilters
from services.analyzer import OddsAnalyzer
from services.scanner import OddsScanner
from ui.dashboard import DashboardView
from ui.game_detail import GameDetailView
from ui.scanner_view import ScannerView
from ui.settings_view import SettingsView


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("OddScope")
        self.resize(1300, 820)

        container = QWidget()
        layout = QHBoxLayout(container)
        self.sidebar = QListWidget()
        for name in ["Dashboard", "Game Detail", "Scanner", "Settings"]:
            self.sidebar.addItem(QListWidgetItem(name))
        self.stack = QStackedWidget()
        self.dashboard = DashboardView()
        self.game_detail = GameDetailView()
        self.scanner_view = ScannerView()
        self.settings_view = SettingsView()
        self.stack.addWidget(self.dashboard)
        self.stack.addWidget(self.game_detail)
        self.stack.addWidget(self.scanner_view)
        self.stack.addWidget(self.settings_view)

        main_layout = QVBoxLayout()
        main_layout.addWidget(self.stack)
        disclaimer = QLabel(
            "Informational analysis only. No guaranteed outcomes. "
            "OddScope does NOT place bets. Bet responsibly."
        )
        disclaimer.setAlignment(Qt.AlignCenter)
        disclaimer.setStyleSheet("color: #9da7b3; font-size: 11px;")
        main_layout.addWidget(disclaimer)

        content_widget = QWidget()
        content_widget.setLayout(main_layout)

        layout.addWidget(self.sidebar, stretch=1)
        layout.addWidget(content_widget, stretch=5)
        self.setCentralWidget(container)

        bundle = build_provider_bundle()
        self.analyzer = OddsAnalyzer(bundle)
        self.scanner = OddsScanner(self.analyzer)

        self.sidebar.currentRowChanged.connect(self.stack.setCurrentIndex)
        self.game_detail.league_picker.currentIndexChanged.connect(self._update_games)
        self.game_detail.game_picker.currentIndexChanged.connect(self._update_game_detail)
        self.game_detail.market_picker.currentIndexChanged.connect(self._update_game_detail)
        self.scanner_view.scan_button.clicked.connect(self._run_scan)

        self.sidebar.setCurrentRow(0)
        self._update_games()
        self._refresh_dashboard()

    def _update_games(self) -> None:
        league = self.game_detail.league_picker.currentData() or League.NBA
        games = self.analyzer.providers.sports.list_games(league)
        self.game_detail.update_games(games)
        if games:
            self.game_detail.game_picker.setCurrentIndex(0)
            self._update_game_detail()

    def _update_game_detail(self) -> None:
        league = self.game_detail.league_picker.currentData() or League.NBA
        game_id = self.game_detail.game_picker.currentData()
        if not game_id:
            return
        analysis = self.analyzer.analyze_game(league, game_id)
        snapshots = self.analyzer.list_snapshots(league)
        self.game_detail.update_analysis(analysis, snapshots)

    def _run_scan(self) -> None:
        filters = ScannerFilters(
            league=self.scanner_view.league_picker.currentData(),
            market=self.scanner_view.market_picker.currentData(),
            min_confidence=float(self.scanner_view.min_confidence.value()),
            min_edge=float(self.scanner_view.min_edge.value()),
            books=self.scanner_view.selected_books(),
        )
        results = self.scanner.scan(filters)
        self.scanner_view.update_results(results)

    def _refresh_dashboard(self) -> None:
        confident = self.scanner.top_confident(5)
        value = self.scanner.top_value(5)
        movement = self.analyzer.list_snapshots(League.NBA)
        self.dashboard.update_tables(confident, value)
        self.dashboard.update_movement_chart(movement)

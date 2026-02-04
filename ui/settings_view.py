from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFormLayout,
    QGroupBox,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from models.types import League, OddsFormat


class SettingsView(QWidget):
    def __init__(self) -> None:
        super().__init__()
        layout = QVBoxLayout(self)

        api_group = QGroupBox("API Keys")
        api_form = QFormLayout()
        self.odds_api_key = QLineEdit()
        self.stats_api_key = QLineEdit()
        api_form.addRow("Odds API Key", self.odds_api_key)
        api_form.addRow("Sports Stats API Key", self.stats_api_key)
        api_group.setLayout(api_form)
        layout.addWidget(api_group)

        pref_group = QGroupBox("Preferences")
        pref_form = QFormLayout()
        self.refresh_interval = QSpinBox()
        self.refresh_interval.setRange(15, 3600)
        self.refresh_interval.setValue(60)
        self.odds_format = QLineEdit(OddsFormat.AMERICAN.value)
        self.preferred_leagues = QListWidget()
        for league in League:
            item = QListWidgetItem(league.value)
            item.setCheckState(Qt.Checked)
            self.preferred_leagues.addItem(item)
        self.preferred_books = QListWidget()
        for book in ["DraftKings", "FanDuel", "Pinnacle"]:
            item = QListWidgetItem(book)
            item.setCheckState(Qt.Checked)
            self.preferred_books.addItem(item)

        pref_form.addRow("Refresh interval (sec)", self.refresh_interval)
        pref_form.addRow("Odds format", self.odds_format)
        pref_form.addRow(QLabel("Preferred leagues"), self.preferred_leagues)
        pref_form.addRow(QLabel("Preferred books"), self.preferred_books)
        pref_group.setLayout(pref_form)
        layout.addWidget(pref_group)

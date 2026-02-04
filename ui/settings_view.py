from __future__ import annotations

from PySide6.QtWidgets import (
    QFormLayout,
    QLabel,
    QLineEdit,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)


class SettingsView(QWidget):
    def __init__(self) -> None:
        super().__init__()
        layout = QVBoxLayout(self)
        self.form = QFormLayout()
        self.risk_percent = QSpinBox()
        self.risk_percent.setRange(1, 5)
        self.risk_percent.setValue(1)
        self.refresh_rate = QSpinBox()
        self.refresh_rate.setRange(15, 300)
        self.refresh_rate.setValue(60)
        self.alpha_key = QLineEdit()
        self.alpha_key.setPlaceholderText("Optional")
        self.form.addRow("Risk % per trade", self.risk_percent)
        self.form.addRow("Refresh rate (s)", self.refresh_rate)
        self.form.addRow("Alpha Vantage key", self.alpha_key)
        layout.addWidget(QLabel("Settings"))
        layout.addWidget(QWidget())
        layout.addLayout(self.form)

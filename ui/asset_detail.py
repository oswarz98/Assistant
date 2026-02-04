from __future__ import annotations

from typing import List

import pyqtgraph as pg
from PySide6.QtWidgets import (
    QComboBox,
    QFormLayout,
    QLabel,
    QListWidget,
    QHBoxLayout,
    QVBoxLayout,
    QWidget,
)

from models.types import AnalysisResult, MarketType


class AssetDetailView(QWidget):
    def __init__(self) -> None:
        super().__init__()
        layout = QVBoxLayout(self)
        header_layout = QHBoxLayout()

        self.symbol_picker = QComboBox()
        self.market_picker = QComboBox()
        for market in MarketType:
            self.market_picker.addItem(market.value, market)
        header_layout.addWidget(QLabel("Market"))
        header_layout.addWidget(self.market_picker)
        header_layout.addWidget(QLabel("Symbol"))
        header_layout.addWidget(self.symbol_picker)
        layout.addLayout(header_layout)

        self.bias_label = QLabel("Bias: --")
        self.confidence_label = QLabel("Confidence: --")
        self.updated_label = QLabel("Updated: --")
        info_layout = QHBoxLayout()
        info_layout.addWidget(self.bias_label)
        info_layout.addWidget(self.confidence_label)
        info_layout.addWidget(self.updated_label)
        layout.addLayout(info_layout)

        self.chart = pg.PlotWidget(background="#0f1216")
        self.chart.showGrid(x=True, y=True, alpha=0.3)
        layout.addWidget(self.chart, stretch=2)

        detail_layout = QHBoxLayout()
        self.summary_form = QFormLayout()
        self.summary_form.addRow("Entry", QLabel("--"))
        self.summary_form.addRow("Stop", QLabel("--"))
        self.summary_form.addRow("TP Targets", QLabel("--"))
        self.summary_form.addRow("Invalidation", QLabel("--"))
        self.summary_form.addRow("Position size", QLabel("--"))
        self.summary_widget = QWidget()
        self.summary_widget.setLayout(self.summary_form)
        detail_layout.addWidget(self.summary_widget)

        self.notes = QListWidget()
        detail_layout.addWidget(self.notes)
        layout.addLayout(detail_layout)

    def update_symbols(self, symbols: List[str]) -> None:
        self.symbol_picker.clear()
        self.symbol_picker.addItems(symbols)

    def update_analysis(self, analysis: AnalysisResult, prices: List[float]) -> None:
        self.bias_label.setText(f"Bias: {analysis.bias.value}")
        self.confidence_label.setText(f"Confidence: {analysis.confidence:.0f}%")
        self.updated_label.setText(f"Updated: {analysis.updated_at.split('T')[0]}")
        self._set_summary(analysis)
        self._set_notes(analysis)
        self._plot(prices)

    def _set_summary(self, analysis: AnalysisResult) -> None:
        labels = [
            analysis.trade_idea.entry_zone,
            analysis.trade_idea.stop_zone,
            ", ".join(analysis.trade_idea.take_profit_targets),
            analysis.trade_idea.invalidation,
            analysis.trade_idea.position_size_hint,
        ]
        for row in range(self.summary_form.rowCount()):
            label = self.summary_form.itemAt(row, QFormLayout.ItemRole.FieldRole).widget()
            if isinstance(label, QLabel):
                label.setText(labels[row])

    def _set_notes(self, analysis: AnalysisResult) -> None:
        self.notes.clear()
        self.notes.addItem(f"Momentum: {analysis.momentum_notes}")
        self.notes.addItem(f"Volatility: {analysis.volatility_notes}")
        self.notes.addItem(f"Structure: {analysis.structure_notes}")
        for note in analysis.risk_notes:
            self.notes.addItem(f"Risk: {note}")

    def _plot(self, prices: List[float]) -> None:
        self.chart.clear()
        if not prices:
            return
        self.chart.plot(prices, pen=pg.mkPen(color="#1f6feb", width=2))

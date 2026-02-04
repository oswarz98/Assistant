from __future__ import annotations


def dark_theme() -> str:
    return """
    QWidget {
        background-color: #0f1216;
        color: #e6edf3;
        font-family: 'Segoe UI', 'Inter', sans-serif;
        font-size: 13px;
    }
    QLineEdit, QComboBox, QListWidget, QTableWidget, QTextEdit, QSpinBox {
        background-color: #151a21;
        border: 1px solid #263042;
        border-radius: 6px;
        padding: 6px;
    }
    QPushButton {
        background-color: #1f6feb;
        border: none;
        padding: 8px 14px;
        border-radius: 6px;
        color: #ffffff;
        font-weight: 600;
    }
    QPushButton:hover {
        background-color: #2c7df0;
    }
    QHeaderView::section {
        background-color: #151a21;
        padding: 6px;
        border: none;
    }
    QTabBar::tab {
        background-color: #151a21;
        padding: 8px 12px;
        border-radius: 6px;
        margin-right: 6px;
    }
    QTabBar::tab:selected {
        background-color: #1f6feb;
        color: #ffffff;
    }
    """

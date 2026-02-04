from __future__ import annotations

import sys

from PySide6.QtWidgets import QApplication

from ui.main_window import MainWindow
from ui.theme import dark_theme


def main() -> None:
    app = QApplication(sys.argv)
    app.setStyleSheet(dark_theme())
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

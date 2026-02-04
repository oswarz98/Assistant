from __future__ import annotations

from typing import Callable

from PySide6.QtCore import QObject, QThread, Signal


class SchedulerWorker(QObject):
    tick = Signal()

    def __init__(self, interval_seconds: int, callback: Callable[[], None]) -> None:
        super().__init__()
        self.interval_seconds = interval_seconds
        self.callback = callback
        self._running = False

    def start(self) -> None:
        self._running = True
        while self._running:
            self.callback()
            QThread.sleep(self.interval_seconds)

    def stop(self) -> None:
        self._running = False


class SchedulerThread(QThread):
    def __init__(self, interval_seconds: int, callback: Callable[[], None]) -> None:
        super().__init__()
        self.worker = SchedulerWorker(interval_seconds, callback)

    def run(self) -> None:
        self.worker.start()

    def stop(self) -> None:
        self.worker.stop()
        self.quit()
        self.wait()

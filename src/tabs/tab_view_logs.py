from typing import Callable
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QPlainTextEdit, QSizePolicy

class ViewLogsTab(QWidget):
    def __init__(
        self,
        parent: QWidget | None,
        load_daily_logs_display_callback: Callable[[], None],
    ):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        log_selection_layout = QHBoxLayout()
        self.log_project_combo = QComboBox()
        self.log_project_combo.currentIndexChanged.connect(load_daily_logs_display_callback)
        log_selection_layout.addWidget(QLabel("Select Project to View Logs:"))
        log_selection_layout.addWidget(self.log_project_combo)
        log_selection_layout.addStretch()
        layout.addLayout(log_selection_layout)
        self.daily_logs_display = QPlainTextEdit()
        self.daily_logs_display.setReadOnly(True)
        self.daily_logs_display.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        layout.addWidget(self.daily_logs_display)

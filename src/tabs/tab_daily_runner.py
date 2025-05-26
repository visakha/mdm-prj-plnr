from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QDateEdit, QPushButton, QGroupBox, QPlainTextEdit, QFormLayout
from PySide6.QtCore import QDate
from typing import Callable

class DailyRunnerTab(QWidget):
    def __init__(
        self,
        parent: QWidget | None,
        on_log_date_changed: Callable[[], None],
        simulate_next_day: Callable[[], None],
        submit_daily_log: Callable[[], None],
    ):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        top_bar_layout = QHBoxLayout()
        self.current_project_label = QLabel("Current Project: <None Selected>")
        self.current_log_date_display = QDateEdit(QDate.currentDate())
        self.current_log_date_display.setCalendarPopup(True)
        self.current_log_date_display.dateChanged.connect(on_log_date_changed)
        self.simulate_next_day_btn = QPushButton("Simulate Next Day >>")
        self.simulate_next_day_btn.clicked.connect(simulate_next_day)
        top_bar_layout.addWidget(self.current_project_label)
        top_bar_layout.addStretch()
        top_bar_layout.addWidget(QLabel("Logging Date:"))
        top_bar_layout.addWidget(self.current_log_date_display)
        top_bar_layout.addWidget(self.simulate_next_day_btn)
        layout.addLayout(top_bar_layout)
        daily_log_group = QGroupBox("Daily Status Update")
        log_layout = QFormLayout()
        self.activities_us_input = QPlainTextEdit()
        self.activities_india_input = QPlainTextEdit()
        self.blockers_us_input = QPlainTextEdit()
        self.blockers_india_input = QPlainTextEdit()
        self.decisions_made_input = QPlainTextEdit()
        self.next_steps_us_input = QPlainTextEdit()
        self.next_steps_india_input = QPlainTextEdit()
        log_layout.addRow("US Activities:", self.activities_us_input)
        log_layout.addRow("India Activities:", self.activities_india_input)
        log_layout.addRow("US Blockers:", self.blockers_us_input)
        log_layout.addRow("India Blockers:", self.blockers_india_input)
        log_layout.addRow("Decisions Made:", self.decisions_made_input)
        log_layout.addRow("US Next Steps:", self.next_steps_us_input)
        log_layout.addRow("India Next Steps:", self.next_steps_india_input)
        self.submit_daily_log_btn = QPushButton("Submit Daily Log")
        self.submit_daily_log_btn.clicked.connect(submit_daily_log)
        log_layout.addRow("", self.submit_daily_log_btn)
        daily_log_group.setLayout(log_layout)
        layout.addWidget(daily_log_group)
        layout.addStretch()

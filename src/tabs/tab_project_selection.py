from PySide6.QtWidgets import QWidget, QVBoxLayout, QFormLayout, QGroupBox, QComboBox, QLineEdit, QDateEdit, QPushButton
from PySide6.QtCore import QDate
from typing import Callable

class ProjectSelectionTab(QWidget):
    def __init__(
        self,
        parent: QWidget | None,
        on_project_selected: Callable[[], None],
        create_project_callback: Callable[[], None],
    ):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        project_selection_group = QGroupBox("Select or Create Project")
        project_selection_layout = QFormLayout()
        self.project_combo = QComboBox()
        self.project_combo.currentIndexChanged.connect(on_project_selected)
        project_selection_layout.addRow("Select Existing Project:", self.project_combo)
        self.project_name_input = QLineEdit()
        self.project_start_date_input = QDateEdit(QDate.currentDate())
        self.project_start_date_input.setCalendarPopup(True)
        self.project_end_date_target_input = QDateEdit(QDate.currentDate().addMonths(7))
        self.project_end_date_target_input.setCalendarPopup(True)
        self.create_project_btn = QPushButton("Create New Project")
        self.create_project_btn.clicked.connect(create_project_callback)
        project_selection_layout.addRow("New Project Name:", self.project_name_input)
        project_selection_layout.addRow("Project Start Date:", self.project_start_date_input)
        project_selection_layout.addRow("Target End Date (7 months):", self.project_end_date_target_input)
        project_selection_layout.addRow("", self.create_project_btn)
        self.theme_combo: QComboBox = QComboBox()
        self.theme_combo.addItems([
            "dark_amber", "dark_blue", "dark_cyan", "dark_lightgreen", "dark_pink", "dark_purple", "dark_red", "dark_teal", "dark_yellow",
            "light_amber", "light_blue_500", "light_blue", "light_cyan_500", "light_cyan", "light_lightgreen_500", "light_lightgreen", "light_orange", "light_pink_500", "light_pink", "light_purple_500", "light_purple", "light_red_500", "light_red", "light_teal_500", "light_teal", "light_yellow"
        ])
        project_selection_layout.addRow("Theme:", self.theme_combo)
        project_selection_group.setLayout(project_selection_layout)
        layout.addWidget(project_selection_group)
        layout.addStretch()

    def _on_theme_changed(self):
        # Call parent's theme change handler if available
        if hasattr(self.parent(), 'on_theme_changed'):
            self.parent().on_theme_changed(self.theme_combo.currentText())

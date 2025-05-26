from typing import Callable
from config import ConfigManager
from PySide6.QtWidgets import QWidget, QVBoxLayout, QFormLayout, QGroupBox, QLabel, QLineEdit, QPushButton

class PropertiesTab(QWidget):
    def __init__(
        self,
        parent: QWidget | None,
        config_manager: ConfigManager,
        save_properties_callback: Callable[[], None],
    ):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        self.properties_form_layout = QFormLayout()
        self.property_inputs: dict[tuple[str, str], QLineEdit] = {}
        for section in config_manager.config.sections():
            group_box = QGroupBox(section.replace('_', ' ').title())
            group_layout = QFormLayout()
            for key, value in config_manager.config.items(section):
                label = QLabel(key.replace('_', ' ').title() + ":")
                input_field = QLineEdit(value)
                group_layout.addRow(label, input_field)
                self.property_inputs[(section, key)] = input_field
            group_box.setLayout(group_layout)
            self.properties_form_layout.addRow(group_box)
        self.save_properties_btn = QPushButton("Save Properties")
        self.save_properties_btn.clicked.connect(save_properties_callback)
        self.properties_form_layout.addRow("", self.save_properties_btn)
        layout.addLayout(self.properties_form_layout)
        layout.addStretch()

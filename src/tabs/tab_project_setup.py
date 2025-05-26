from typing import Callable
from PySide6.QtWidgets import QWidget, QVBoxLayout, QGroupBox, QTreeWidget, QHeaderView, QHBoxLayout, QPushButton, QSizePolicy

class ProjectSetupTab(QWidget):
    def __init__(
        self,
        parent: QWidget | None,
        show_add_phase: Callable[[], None],
        show_add_epic: Callable[[], None],
        show_add_task: Callable[[], None],
        add_initial_plan: Callable[[], None],
    ):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        plan_group = QGroupBox()
        plan_group.setFlat(True)
        plan_group.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        plan_layout = QVBoxLayout()
        plan_layout.setContentsMargins(0, 0, 0, 0)
        plan_layout.setSpacing(0)
        self.project_plan_tree = QTreeWidget()
        self.project_plan_tree.setHeaderLabels(["Item", "Description", "Assigned To", "Status", "Due Date"])  # type: ignore
        self.project_plan_tree.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.project_plan_tree.header().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.project_plan_tree.header().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        plan_layout.addWidget(self.project_plan_tree, stretch=1)
        plan_buttons_layout = QHBoxLayout()
        self.add_phase_btn = QPushButton("Add Phase")
        self.add_phase_btn.clicked.connect(show_add_phase)
        self.add_epic_btn = QPushButton("Add Epic")
        self.add_epic_btn.clicked.connect(show_add_epic)
        self.add_task_btn = QPushButton("Add Task")
        self.add_task_btn.clicked.connect(show_add_task)
        self.add_initial_plan_btn = QPushButton("Auto-Populate Project Plan")
        self.add_initial_plan_btn.clicked.connect(add_initial_plan)
        plan_buttons_layout.addWidget(self.add_phase_btn)
        plan_buttons_layout.addWidget(self.add_epic_btn)
        plan_buttons_layout.addWidget(self.add_task_btn)
        plan_buttons_layout.addStretch()
        plan_buttons_layout.addWidget(self.add_initial_plan_btn)
        plan_layout.addLayout(plan_buttons_layout)
        plan_group.setLayout(plan_layout)
        layout.addWidget(plan_group, stretch=1)

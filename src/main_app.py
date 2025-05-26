# main_app.py
import sys
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QTextEdit, # type: ignore
    QDateEdit,
    QTabWidget,
    QFormLayout,
    QGroupBox,
    QComboBox,
    QPlainTextEdit,
    QMessageBox,
    QTreeWidget,
    QTreeWidgetItem,
    QHeaderView,
    QSizePolicy,
)
from PySide6.QtCore import QDate, Qt # type: ignore
from PySide6.QtGui import QIcon, QFont # type: ignore
from PySide6.QtCore import QCoreApplication  # type: ignore # Explicitly import for QApplication

from datetime import date, timedelta
from typing import Optional, Dict, Tuple, List 

from database import ProjectManagerDB, Project, Phase, Epic,  DailyLog #Task, SubTask,
from config import ConfigManager


class ProjectPlannerApp(QMainWindow):
    """
    Main application window for the Project Planning & Daily Runner.
    Provides tabs for Project Setup, Daily Runner, Properties, and Log Viewer.
    """

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Project Planning & Daily Runner for ETL/MDM")
        self.setGeometry(100, 100, 1200, 800)  # x, y, width, height

        # Initialize database and config managers
        self.db_manager: ProjectManagerDB = ProjectManagerDB()
        self.config_manager: ConfigManager = ConfigManager()

        # State variables
        self._current_project_id: Optional[int] = None
        self._current_log_date: QDate = QDate.currentDate()  # For the daily runner tab

        # UI Widgets (declared with type hints for clarity)
        self.project_combo: QComboBox
        self.project_name_input: QLineEdit
        self.project_start_date_input: QDateEdit
        self.project_end_date_target_input: QDateEdit
        self.create_project_btn: QPushButton
        self.project_plan_tree: QTreeWidget
        self.add_phase_btn: QPushButton
        self.add_epic_btn: QPushButton
        self.add_task_btn: QPushButton
        self.add_initial_plan_btn: QPushButton
        self.current_project_label: QLabel
        self.current_log_date_display: QDateEdit
        self.simulate_next_day_btn: QPushButton
        self.activities_us_input: QPlainTextEdit
        self.activities_india_input: QPlainTextEdit
        self.blockers_us_input: QPlainTextEdit
        self.blockers_india_input: QPlainTextEdit
        self.decisions_made_input: QPlainTextEdit
        self.next_steps_us_input: QPlainTextEdit
        self.next_steps_india_input: QPlainTextEdit
        self.submit_daily_log_btn: QPushButton
        self.property_inputs: Dict[Tuple[str, str], QLineEdit] = {}
        self.save_properties_btn: QPushButton
        self.log_project_combo: QComboBox
        self.daily_logs_display: QPlainTextEdit

        self._setup_ui()
        self._load_initial_data()  # Populate project dropdowns

    def _setup_ui(self) -> None:
        """Sets up the main window's user interface."""
        self.central_widget: QWidget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout: QVBoxLayout = QVBoxLayout(self.central_widget)

        # Main Tab Widget
        self.tab_widget: QTabWidget = QTabWidget()
        self.main_layout.addWidget(self.tab_widget)

        # --- Project Setup Tab ---
        self.project_setup_tab: QWidget = QWidget()
        self.tab_widget.addTab(self.project_setup_tab, "1. Project Setup & Plan")
        self._setup_project_setup_tab()

        # --- Daily Runner Tab ---
        self.daily_runner_tab: QWidget = QWidget()
        self.tab_widget.addTab(self.daily_runner_tab, "2. Daily Runner")
        self._setup_daily_runner_tab()

        # --- Properties Tab ---
        self.properties_tab: QWidget = QWidget()
        self.tab_widget.addTab(self.properties_tab, "3. Application Properties")
        self._setup_properties_tab()

        # --- View Logs Tab ---
        self.view_logs_tab: QWidget = QWidget()
        self.tab_widget.addTab(self.view_logs_tab, "4. View Daily Logs")
        self._setup_view_logs_tab()

    def _show_add_phase_dialog(self) -> None:
        """Placeholder for Add Phase dialog (not yet implemented)."""
        QMessageBox.information(self, "Not Implemented", "Add Phase dialog is not implemented yet.")

    def _show_add_epic_dialog(self) -> None:
        """Placeholder for Add Epic dialog (not yet implemented)."""
        QMessageBox.information(self, "Not Implemented", "Add Epic dialog is not implemented yet.")

    def _show_add_task_dialog(self) -> None:
        """Placeholder for Add Task dialog (not yet implemented)."""
        QMessageBox.information(self, "Not Implemented", "Add Task dialog is not implemented yet.")

    def _setup_project_setup_tab(self) -> None:
        """Sets up the Project Setup & Plan tab."""
        layout: QVBoxLayout = QVBoxLayout(self.project_setup_tab)

        # Project Selection / Creation Group
        project_selection_group: QGroupBox = QGroupBox("Select or Create Project")
        project_selection_layout: QFormLayout = QFormLayout()
        self.project_combo = QComboBox()
        self.project_combo.currentIndexChanged.connect(self._on_project_selected)
        project_selection_layout.addRow("Select Existing Project:", self.project_combo)

        self.project_name_input = QLineEdit()
        self.project_start_date_input = QDateEdit(QDate.currentDate())
        self.project_start_date_input.setCalendarPopup(True)
        # Calculate 7 months from current date for target end date
        self.project_end_date_target_input = QDateEdit(QDate.currentDate().addMonths(7))
        self.project_end_date_target_input.setCalendarPopup(True)
        self.create_project_btn = QPushButton("Create New Project")
        self.create_project_btn.clicked.connect(self._create_new_project)

        project_selection_layout.addRow("New Project Name:", self.project_name_input)
        project_selection_layout.addRow("Project Start Date:", self.project_start_date_input)
        project_selection_layout.addRow(
            "Target End Date (7 months):", self.project_end_date_target_input
        )
        project_selection_layout.addRow("", self.create_project_btn)
        project_selection_group.setLayout(project_selection_layout)
        layout.addWidget(project_selection_group)

        # Initial Project Plan Group
        plan_group: QGroupBox = QGroupBox("Project Plan Structure (Phases, Epics, Tasks)")
        plan_layout: QVBoxLayout = QVBoxLayout()
        plan_layout.addWidget(QLabel("This section allows you to define your project hierarchy."))

        # Tree view for project plan
        self.project_plan_tree = QTreeWidget()
        self.project_plan_tree.setHeaderLabels(["Item", "Description", "Assigned To", "Status", "Due Date"])  # type: ignore
        self.project_plan_tree.header().setSectionResizeMode(
            0, QHeaderView.ResizeMode.ResizeToContents
        )
        self.project_plan_tree.header().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        plan_layout.addWidget(self.project_plan_tree)

        # Buttons for adding plan elements (currently placeholder, auto-populate used)
        plan_buttons_layout: QHBoxLayout = QHBoxLayout()
        # Add Phase Button
        self.add_phase_btn = QPushButton("Add Phase")
        self.add_phase_btn.clicked.connect(self._show_add_phase_dialog)

        # Add Epic Button
        self.add_epic_btn = QPushButton("Add Epic")
        self.add_epic_btn.clicked.connect(self._show_add_epic_dialog)

        # Add Task Button
        self.add_task_btn = QPushButton("Add Task")
        self.add_task_btn.clicked.connect(self._show_add_task_dialog)
        
        self.add_initial_plan_btn = QPushButton("Auto-Populate Project Plan")
        self.add_initial_plan_btn.clicked.connect(self._add_initial_project_plan)

        plan_buttons_layout.addWidget(self.add_phase_btn)
        plan_buttons_layout.addWidget(self.add_epic_btn)
        plan_buttons_layout.addWidget(self.add_task_btn)
        plan_buttons_layout.addStretch()
        plan_buttons_layout.addWidget(self.add_initial_plan_btn)

        plan_layout.addLayout(plan_buttons_layout)
        plan_group.setLayout(plan_layout)
        layout.addWidget(plan_group)

        layout.addStretch()

    def _setup_daily_runner_tab(self) -> None:
        """Sets up the Daily Runner tab for logging daily activities."""
        layout: QVBoxLayout = QVBoxLayout(self.daily_runner_tab)

        # Current Project and Date Display
        top_bar_layout: QHBoxLayout = QHBoxLayout()
        self.current_project_label = QLabel("Current Project: <None Selected>")
        self.current_project_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))  # type: ignore
        self.current_log_date_display = QDateEdit(self._current_log_date)
        self.current_log_date_display.setCalendarPopup(True)
        self.current_log_date_display.dateChanged.connect(self._on_log_date_changed)
        self.simulate_next_day_btn = QPushButton("Simulate Next Day >>")
        self.simulate_next_day_btn.clicked.connect(self._simulate_next_day)

        top_bar_layout.addWidget(self.current_project_label)
        top_bar_layout.addStretch()
        top_bar_layout.addWidget(QLabel("Logging Date:"))
        top_bar_layout.addWidget(self.current_log_date_display)
        top_bar_layout.addWidget(self.simulate_next_day_btn)
        layout.addLayout(top_bar_layout)

        # Daily Status Update Group
        daily_log_group: QGroupBox = QGroupBox("Daily Status Update")
        log_layout: QFormLayout = QFormLayout()

        self.activities_us_input = QPlainTextEdit()
        self.activities_us_input.setPlaceholderText(
            "Activities by USA Team (SSA1, SA2) - e.g., 'Conducted client workshop on MDM UI requirements.'"
        )
        self.activities_india_input = QPlainTextEdit()
        self.activities_india_input.setPlaceholderText(
            "Activities by India Team - e.g., 'Started development for Ingress Source 1 data mapping.'"
        )
        self.blockers_us_input = QPlainTextEdit()
        self.blockers_us_input.setPlaceholderText(
            "Blockers for USA Team - e.g., 'Awaiting client approval on data model changes.'"
        )
        self.blockers_india_input = QPlainTextEdit()
        self.blockers_india_input.setPlaceholderText(
            "Blockers for India Team - e.g., 'Need clarification on transformation logic for field X.'"
        )
        self.decisions_made_input = QPlainTextEdit()
        self.decisions_made_input.setPlaceholderText(
            "Key Decisions Made - e.g., 'Agreed to use workaround Y for vendor product limitation.'"
        )
        self.next_steps_us_input = QPlainTextEdit()
        self.next_steps_us_input.setPlaceholderText(
            "Next Steps for USA Team - e.g., 'Prepare design for Egress module.'"
        )
        self.next_steps_india_input = QPlainTextEdit()
        self.next_steps_india_input.setPlaceholderText(
            "Next Steps for India Team - e.g., 'Complete unit tests for Ingress Source 1.'"
        )

        log_layout.addRow("US Activities:", self.activities_us_input)
        log_layout.addRow("India Activities:", self.activities_india_input)
        log_layout.addRow("US Blockers:", self.blockers_us_input)
        log_layout.addRow("India Blockers:", self.blockers_india_input)
        log_layout.addRow("Decisions Made:", self.decisions_made_input)
        log_layout.addRow("US Next Steps:", self.next_steps_us_input)
        log_layout.addRow("India Next Steps:", self.next_steps_india_input)

        self.submit_daily_log_btn = QPushButton("Submit Daily Log")
        self.submit_daily_log_btn.clicked.connect(self._submit_daily_log)
        log_layout.addRow("", self.submit_daily_log_btn)

        daily_log_group.setLayout(log_layout)
        layout.addWidget(daily_log_group)
        layout.addStretch()

    def _setup_properties_tab(self) -> None:
        """Sets up the Application Properties tab."""
        layout: QVBoxLayout = QVBoxLayout(self.properties_tab)
        self.properties_form_layout: QFormLayout = QFormLayout()

        # Load all properties from config and add to form
        for section in self.config_manager.config.sections():
            group_box: QGroupBox = QGroupBox(section.replace('_', ' ').title())
            group_layout: QFormLayout = QFormLayout()
            for key, value in self.config_manager.config.items(section):
                label: QLabel = QLabel(key.replace('_', ' ').title() + ":")
                input_field: QLineEdit = QLineEdit(value)
                group_layout.addRow(label, input_field)
                self.property_inputs[(section, key)] = input_field
            group_box.setLayout(group_layout)
            self.properties_form_layout.addRow(group_box)

        self.save_properties_btn = QPushButton("Save Properties")
        self.save_properties_btn.clicked.connect(self._save_properties)
        self.properties_form_layout.addRow("", self.save_properties_btn)

        layout.addLayout(self.properties_form_layout)
        layout.addStretch()

    def _setup_view_logs_tab(self) -> None:
        """Sets up the View Daily Logs tab."""
        layout: QVBoxLayout = QVBoxLayout(self.view_logs_tab)

        log_selection_layout: QHBoxLayout = QHBoxLayout()
        self.log_project_combo = QComboBox()
        self.log_project_combo.currentIndexChanged.connect(self._load_daily_logs_display)
        log_selection_layout.addWidget(QLabel("Select Project to View Logs:"))
        log_selection_layout.addWidget(self.log_project_combo)
        log_selection_layout.addStretch()
        layout.addLayout(log_selection_layout)

        self.daily_logs_display = QPlainTextEdit()
        self.daily_logs_display.setReadOnly(True)
        self.daily_logs_display.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        layout.addWidget(self.daily_logs_display)

    # --- Core Logic Methods ---

    def _load_initial_data(self) -> None:
        """Populates project dropdowns on application startup."""
        self._populate_project_combos()

    def _populate_project_combos(self) -> None:
        """Refreshes the project dropdowns in Project Setup and View Logs tabs."""
        self.project_combo.clear()
        self.log_project_combo.clear()
        projects: List[Project] = self.db_manager.get_all_projects()
        if not projects:
            self.project_combo.addItem("No Projects Yet - Create One!")
            self.project_combo.setEnabled(False)
            self.log_project_combo.addItem("No Projects Yet")
            self.log_project_combo.setEnabled(False)
            self._current_project_id = None
            self.current_project_label.setText("Current Project: <None Selected>")
            self.project_plan_tree.clear() # Clear tree if no projects
        else:
            self.project_combo.setEnabled(True)
            self.log_project_combo.setEnabled(True)
            for project in projects:
                self.project_combo.addItem(project.name, userData=project.id)
                self.log_project_combo.addItem(project.name, userData=project.id)
            # Set initial selection to the first project if available
            self.project_combo.setCurrentIndex(0) # Triggers _on_project_selected
            # The _on_project_selected will handle setting _current_project_id and loading plan/logs

    def _on_project_selected(self) -> None:
        """Handles project selection change in the Project Setup tab."""
        project_id: Optional[int] = self.project_combo.currentData()
        if project_id is not None:
            self._current_project_id = project_id
            self.current_project_label.setText(f"Current Project: {self.project_combo.currentText()}")
            self._load_project_plan_tree() # Load plan for the newly selected project
            # Ensure the log combo also reflects the current project
            if self.log_project_combo.currentData() != project_id:
                index: int = self.log_project_combo.findData(project_id)
                if index != -1:
                    self.log_project_combo.setCurrentIndex(index)
            else:
                self._load_daily_logs_display() # Reload logs if it's the same project
        else:
            self._current_project_id = None
            self.current_project_label.setText("Current Project: <None Selected>")
            self.project_plan_tree.clear() # Clear tree if no project is selected

    def _create_new_project(self) -> None:
        """Creates a new project based on user input."""
        name: str = self.project_name_input.text().strip()
        start_date_q: QDate = self.project_start_date_input.date()
        end_date_target_q: QDate = self.project_end_date_target_input.date()

        if not name:
            QMessageBox.warning(self, "Input Error", "Project name cannot be empty.")
            return

        start_date_py: date = date(start_date_q.year(), start_date_q.month(), start_date_q.day())
        end_date_target_py: date = date(end_date_target_q.year(), end_date_target_q.month(), end_date_target_q.day())

        existing_project: Optional[Project] = self.db_manager.get_project_by_name(name)
        if existing_project:
            QMessageBox.warning(self, "Duplicate Project", f"Project with name '{name}' already exists.")
            return

        try:
            project: Project = self.db_manager.create_project(name, start_date_py, end_date_target_py)
            QMessageBox.information(self, "Success", f"Project '{project.name}' created successfully!")
            self.project_name_input.clear()
            self._populate_project_combos() # Refresh combos and select new project
        except Exception as e:
            QMessageBox.critical(self, "Database Error", f"Failed to create project: {e}")

    def _load_project_plan_tree(self) -> None:
        """Loads and displays the project plan (phases, epics, tasks) in the tree view."""
        self.project_plan_tree.clear()
        if self._current_project_id is None:
            return

        session = self.db_manager.get_session()
        project: Optional[Project] = session.query(Project).get(self._current_project_id)

        if not project:
            session.close()
            return

        for phase in project.phases:
            phase_item: QTreeWidgetItem = QTreeWidgetItem(
                self.project_plan_tree, [phase.name, phase.description, "", "", ""]
            )
            for epic in phase.epics:
                epic_item: QTreeWidgetItem = QTreeWidgetItem(
                    phase_item, [epic.name, epic.description, "", epic.status, ""]
                )
                for task in epic.tasks:
                    task_due_date: str = (
                        task.due_date.strftime("%Y-%m-%d") if task.due_date else "N/A"
                    )
                    task_item: QTreeWidgetItem = QTreeWidgetItem(
                        epic_item,
                        [task.name, task.description, task.assigned_to, task.status, task_due_date],
                    )
                    for subtask in task.subtasks:
                        subtask_item: QTreeWidgetItem = QTreeWidgetItem( # type: ignore
                            task_item,
                            [
                                subtask.name,
                                subtask.description,
                                subtask.assigned_to,
                                subtask.status,
                                "",
                            ],
                        )
        session.close()
        self.project_plan_tree.expandAll() # Expand all items for better visibility

    def _add_initial_project_plan(self) -> None:
        """
        Auto-populates the selected project with a default plan structure
        based on the project description and config settings.
        """
        if self._current_project_id is None:
            QMessageBox.warning(self, "No Project Selected", "Please select or create a project first.")
            return

        project: Optional[Project] = self.db_manager.get_project_by_name(self.project_combo.currentText())
        if not project:
            QMessageBox.critical(self, "Error", "Selected project not found in database.")
            return

        reply: QMessageBox.StandardButton = QMessageBox.question(self, "Confirm Auto-Populate",
                                         "This will add a default plan structure (Phases, Epics, Tasks) to the current project. Continue?",
                                         QMessageBox.Yes | QMessageBox.No) # type: ignore
        if reply == QMessageBox.No: # type: ignore
            return

        try:
            ssa1_name: Optional[str] = self.config_manager.get_property('TEAM_MEMBERS', 'SSA1_Name')
            sa2_name: Optional[str] = self.config_manager.get_property('TEAM_MEMBERS', 'SA2_Name')
            offshore_pm_name: Optional[str] = self.config_manager.get_property('TEAM_MEMBERS', 'Offshore_PM_Name')

            # Provide default empty strings if names are None from config
            ssa1_name_str: str = ssa1_name if ssa1_name is not None else "SSA1"
            sa2_name_str: str = sa2_name if sa2_name is not None else "SA2"
            offshore_pm_name_str: str = offshore_pm_name if offshore_pm_name is not None else "Offshore PM"


            # Phase 1: Inception & Detailed Planning (Weeks 1-4)
            phase1: Phase = self.db_manager.add_phase(
                project.id,
                "Phase 1: Inception & Detailed Planning (Weeks 1-4)",
                "Establish foundational understanding, detailed requirements, and initial design for key modules.",
                start_date=project.start_date,
                end_date=project.start_date + timedelta(weeks=4)
            )
            epic1_1: Epic = self.db_manager.add_epic(
                phase1.id,
                "Requirements Gathering & Reverse Engineering",
                "Gather business & technical requirements, reverse engineer vendor product.",
            )
            self.db_manager.add_task(
                epic1_1.id,
                "Client Kick-off & Expectations Alignment",
                "Formal kick-off with client to align on scope and communication.",
                ssa1_name_str,
                "High",
                due_date=project.start_date + timedelta(days=3),
            )
            self.db_manager.add_task(
                epic1_1.id,
                "Vendor Product Architecture Deep Dive",
                "Dissect existing on-prem MDM product for architecture, APIs, and customization points.",
                f"{ssa1_name_str}, {sa2_name_str}",
                "High",
                due_date=project.start_date + timedelta(days=7),
            )
            self.db_manager.add_task(
                epic1_1.id,
                "Detailed MDM Customization Requirements",
                "Workshops with client BAs for data quality, validations, UI, RBAC.",
                ssa1_name_str,
                "High",
                due_date=project.start_date + timedelta(days=14),
            )
            self.db_manager.add_task(
                epic1_1.id,
                "Ingress Source System Data Mapping (Initial 5)",
                "Detailed data mapping for the first 5 critical ingress sources.",
                sa2_name_str,
                "High",
                due_date=project.start_date + timedelta(days=14),
            )

            epic1_2: Epic = self.db_manager.add_epic(phase1.id, "Technical Design & Initial POCs", "Develop overall architectural design and conduct critical proof of concepts.")
            self.db_manager.add_task(epic1_2.id, "Overall ETL/MDM Solution Architecture", "Design the end-to-end architecture for Ingress, MDM, and Egress.", ssa1_name_str, 'High', due_date=project.start_date + timedelta(days=21))
            self.db_manager.add_task(epic1_2.id, "MDM Customization Framework POC", "Prove out a customization approach for the vendor MDM product.", sa2_name_str, 'High', due_date=project.start_date + timedelta(days=21))
            self.db_manager.add_task(epic1_2.id, "Ingress Data Pipeline POC (Connector)", "Validate connectivity and initial data extraction from a complex source.", sa2_name_str, 'Medium', due_date=project.start_date + timedelta(days=28))
            self.db_manager.add_task(epic1_2.id, "Offshore Team Onboarding & Environment Setup", "Ensure offshore team has access, tools, and dev environments ready.", offshore_pm_name_str, 'High', due_date=project.start_date + timedelta(days=28))


            # Phase 2: Iterative Development & Delivery (Months 2-6)
            phase2: Phase = self.db_manager.add_phase(
                project.id,
                "Phase 2: Iterative Development & Delivery (Months 2-6)",
                "Develop, unit test, and deliver functional modules in iterations.",
                start_date=project.start_date + timedelta(weeks=4),
                end_date=project.start_date + timedelta(weeks=4 + 5*4) # 5 months
            )
            epic2_1: Epic = self.db_manager.add_epic(phase2.id, "Ingress Module Development", "Develop data pipelines for 20 source systems into MDM.")
            self.db_manager.add_task(epic2_1.id, "Ingress Source 1-5 Development & Unit Test", "Develop and unit test pipelines for first 5 critical sources.", offshore_pm_name_str + ' (Offshore Team)', 'High')
            self.db_manager.add_task(epic2_1.id, "Ingress Source 6-10 Development & Unit Test", "Develop and unit test pipelines for next 5 critical sources.", offshore_pm_name_str + ' (Offshore Team)', 'Medium')
            self.db_manager.add_task(epic2_1.id, "Ingress Source 11-20 Development & Unit Test", "Develop and unit test pipelines for remaining sources.", offshore_pm_name_str + ' (Offshore Team)', 'Low')
            self.db_manager.add_task(epic2_1.id, "Ingress Data Quality & Error Handling", "Implement robust data quality checks and error logging for all pipelines.", sa2_name_str, 'High')

            epic2_2: Epic = self.db_manager.add_epic(phase2.id, "Egress Module Development", "Pull data from CRM, identify deltas, and write to CSV files.")
            self.db_manager.add_task(epic2_2.id, "Egress CRM Data Extraction Design", "Design efficient extraction of CRM data.", sa2_name_str, 'High')
            self.db_manager.add_task(epic2_2.id, "Egress Delta Logic Implementation", "Implement logic to identify and process data deltas.", offshore_pm_name_str + ' (Offshore Team)', 'High')
            self.db_manager.add_task(epic2_2.id, "Egress CSV File Generation", "Develop module to generate formatted CSV files.", offshore_pm_name_str + ' (Offshore Team)', 'Medium')

            epic2_3: Epic = self.db_manager.add_epic(phase2.id, "MDM Customization & Configuration", "Implement Data Quality, Validations, UI, RBAC based on requirements.")
            self.db_manager.add_task(epic2_3.id, "MDM Data Quality Rules Implementation", "Implement core data quality rules within MDM.", offshore_pm_name_str + ' (Offshore Team)', 'High')
            self.db_manager.add_task(epic2_3.id, "MDM Data Validation Logic", "Implement custom data validation rules.", offshore_pm_name_str + ' (Offshore Team)', 'High')
            self.db_manager.add_task(epic2_3.id, "MDM UI Customization (Key Screens)", "Customize essential UI screens for data stewardship.", offshore_pm_name_str + ' (Offshore Team)', 'Medium')
            self.db_manager.add_task(epic2_3.id, "MDM RBAC Configuration & Testing", "Configure Role-Based Access Control and test permissions.", sa2_name_str, 'High')
            self.db_manager.add_task(epic2_3.id, "MDM Workflow Customization (if applicable)", "Customize data approval/stewardship workflows.", offshore_pm_name_str + ' (Offshore Team)', 'Medium')

            # Phase 3: UAT & Deployment Readiness (Month 7)
            phase3: Phase = self.db_manager.add_phase(
                project.id,
                "Phase 3: UAT & Deployment Readiness (Month 7)",
                "Achieve client sign-off on functionality, prepare for production deployment.",
                start_date=project.start_date + timedelta(weeks=4 + 5*4),
                end_date=project.end_date_target
            )
            epic3_1: Epic = self.db_manager.add_epic(phase3.id, "User Acceptance Testing (UAT)", "Client-led testing and defect resolution.")
            self.db_manager.add_task(epic3_1.id, "UAT Test Case Review & Preparation", "Work with client BAs to finalize UAT test cases.", ssa1_name_str, 'High')
            self.db_manager.add_task(epic3_1.id, "UAT Environment Setup & Data Load", "Prepare and load data into UAT environment.", sa2_name_str, 'High')
            self.db_manager.add_task(epic3_1.id, "UAT Defect Triage & Resolution Cycles", "Manage, prioritize, and resolve defects found during UAT.", f"{offshore_pm_name_str} (Offshore Team), {ssa1_name_str}", 'High')

            epic3_2: Epic = self.db_manager.add_epic(phase3.id, "Deployment Readiness & Go-Live", "Final preparations for production deployment.")
            self.db_manager.add_task(epic3_2.id, "Production Deployment Plan", "Develop detailed plan including rollback strategy.", ssa1_name_str, 'High')
            self.db_manager.add_task(epic3_2.id, "Pre-Go-Live System Health Checks", "Perform final checks on performance, data integrity.", sa2_name_str, 'High')
            self.db_manager.add_task(epic3_2.id, "Post-Go-Live Support Plan", "Define support structure for immediate post-deployment.", ssa1_name_str, 'High')

            QMessageBox.information(self, "Success", "Initial project plan (Phases, Epics, Tasks) added successfully!")
            self._load_project_plan_tree() # Refresh the tree view
        except Exception as e:
            QMessageBox.critical(self, "Error Adding Plan", f"Failed to add initial plan: {e}")
            # Optionally, you might want to rollback changes if multiple DB operations fail

    def _submit_daily_log(self) -> None:
        """Submits the daily log entry to the database."""
        if self._current_project_id is None:
            QMessageBox.warning(self, "No Project Selected", "Please select a project before submitting a daily log.")
            return

        activities_us: str = self.activities_us_input.toPlainText().strip()
        activities_india: str = self.activities_india_input.toPlainText().strip()
        blockers_us: str = self.blockers_us_input.toPlainText().strip()
        blockers_india: str = self.blockers_india_input.toPlainText().strip()
        decisions_made: str = self.decisions_made_input.toPlainText().strip()
        next_steps_us: str = self.next_steps_us_input.toPlainText().strip()
        next_steps_india: str = self.next_steps_india_input.toPlainText().strip()

        # Get the date from the QDateEdit for the log entry
        log_date_py: date = date(self._current_log_date.year(), self._current_log_date.month(), self._current_log_date.day())

        if not (activities_us or activities_india or blockers_us or blockers_india or decisions_made or next_steps_us or next_steps_india):
            QMessageBox.warning(self, "Input Required", "Please enter at least some information for the daily log.")
            return

        try:
            self.db_manager.add_daily_log(
                self._current_project_id,
                activities_us, activities_india,
                blockers_us, blockers_india,
                decisions_made,
                next_steps_us, next_steps_india,
                log_date=log_date_py
            )
            QMessageBox.information(self, "Success", f"Daily log for {log_date_py.strftime('%Y-%m-%d')} submitted successfully!")
            # Clear fields after submission
            self.activities_us_input.clear()
            self.activities_india_input.clear()
            self.blockers_us_input.clear()
            self.blockers_india_input.clear()
            self.decisions_made_input.clear()
            self.next_steps_us_input.clear()
            self.next_steps_india_input.clear()
            self._load_daily_logs_display() # Refresh logs display
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to submit daily log: {e}")

    def _on_log_date_changed(self, new_date: QDate) -> None:
        """Updates the internal log date when the date edit changes."""
        self._current_log_date = new_date

    def _simulate_next_day(self) -> None:
        """Advances the logging date by one day."""
        self._current_log_date = self._current_log_date.addDays(1)
        self.current_log_date_display.setDate(self._current_log_date)
        QMessageBox.information(self, "Date Advanced", f"Logging date advanced to {self._current_log_date.toString('yyyy-MM-dd')}.")
        # Optionally, you could clear the daily log fields here for the new day
        self.activities_us_input.clear()
        self.activities_india_input.clear()
        self.blockers_us_input.clear()
        self.blockers_india_input.clear()
        self.decisions_made_input.clear()
        self.next_steps_us_input.clear()
        self.next_steps_india_input.clear()

    def _save_properties(self) -> None:
        """Saves the updated properties from the UI to the config file."""
        try:
            for (section, key), input_field in self.property_inputs.items():
                self.config_manager.set_property(section, key, input_field.text())
            QMessageBox.information(self, "Success", "Properties saved successfully!")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save properties: {e}")

    def _load_daily_logs_display(self) -> None:
        """Loads and displays daily logs for the selected project in the View Logs tab."""
        project_id: Optional[int] = self.log_project_combo.currentData()
        self.daily_logs_display.clear()
        if project_id is None:
            self.daily_logs_display.setPlainText("No project selected or no logs available.")
            return

        logs: List[DailyLog] = self.db_manager.get_daily_logs_for_project(project_id)
        if not logs:
            self.daily_logs_display.setPlainText("No daily logs found for this project.")
            return

        log_text_parts: List[str] = []
        for log in logs:
            log_text_parts.append(f"--- Log for {log.log_date.strftime('%Y-%m-%d')} (Recorded: {log.timestamp.strftime('%H:%M')}) ---")
            if log.activities_us:
                log_text_parts.append(f"US Activities:\n{log.activities_us}")
            if log.activities_india:
                log_text_parts.append(f"India Activities:\n{log.activities_india}")
            if log.blockers_us:
                log_text_parts.append(f"US Blockers:\n{log.blockers_us}")
            if log.blockers_india:
                log_text_parts.append(f"India Blockers:\n{log.blockers_india}")
            if log.decisions_made:
                log_text_parts.append(f"Decisions Made:\n{log.decisions_made}")
            if log.next_steps_us:
                log_text_parts.append(f"US Next Steps:\n{log.next_steps_us}")
            if log.next_steps_india:
                log_text_parts.append(f"India Next Steps:\n{log.next_steps_india}")
            log_text_parts.append("--------------------------------------------------\n")
        self.daily_logs_display.setPlainText("\n".join(log_text_parts))


if __name__ == "__main__":
    # Ensure a QApplication instance exists before creating QWidgets
    app: QApplication = QApplication(sys.argv)
    window: ProjectPlannerApp = ProjectPlannerApp()
    window.show()
    sys.exit(app.exec())


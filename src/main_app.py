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
    QDialog,
    QDialogButtonBox,
)
from PySide6.QtCore import QDate, Qt # type: ignore
from PySide6.QtGui import QIcon, QFont # type: ignore
from PySide6.QtCore import QCoreApplication  # type: ignore # Explicitly import for QApplication

from datetime import date, timedelta
from typing import Optional, Dict, Tuple, List, Any

from database import ProjectManagerDB, Project, Phase, Epic,  DailyLog #Task, SubTask,
from config import ConfigManager
import qdarktheme # type: ignore 
from PySide6.QtGui import QKeySequence, QShortcut

from tabs.tab_project_selection import ProjectSelectionTab # type: ignore
from tabs.tab_project_setup import ProjectSetupTab # type: ignore
from tabs.tab_daily_runner import DailyRunnerTab # type: ignore
from tabs.tab_properties import PropertiesTab # type: ignore
from tabs.tab_view_logs import ViewLogsTab # type: ignore

class ProjectPlannerApp(QMainWindow):
    """
    Main application window for the Project Planning & Daily Runner.
    Provides tabs for Project Setup, Daily Runner, Properties, and Log Viewer.
    """

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Project Planning & Daily Runner for ETL/MDM")
        self.setGeometry(100, 100, 1200, 800)
        self.showMaximized()  # Start in full screen

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
        # Populate project dropdowns after widgets are wired up
        self._populate_project_combos()

    def _setup_ui(self) -> None:
        """Sets up the main window's user interface."""
        self.central_widget: QWidget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout: QVBoxLayout = QVBoxLayout(self.central_widget)

        # Main Tab Widget
        self.tab_widget: QTabWidget = QTabWidget()
        self.main_layout.addWidget(self.tab_widget)

        # --- Project Selection Tab ---
        self.project_selection_tab = ProjectSelectionTab(
            parent=self,
            on_project_selected=lambda: None,  # Placeholder, will wire up after instantiation
            create_project_callback=lambda: None,
        )
        self.tab_widget.addTab(self.project_selection_tab, "0. Project Selection")

        # --- Project Setup Tab ---
        self.project_setup_tab = ProjectSetupTab(
            parent=self,
            show_add_phase=lambda: None,
            show_add_epic=lambda: None,
            show_add_task=lambda: None,
            add_initial_plan=lambda: None,
        )
        self.tab_widget.addTab(self.project_setup_tab, "1. Project Setup & Plan")

        # --- Daily Runner Tab ---
        self.daily_runner_tab = DailyRunnerTab(
            parent=self,
            on_log_date_changed=lambda: None,
            simulate_next_day=lambda: None,
            submit_daily_log=lambda: None,
        )
        self.tab_widget.addTab(self.daily_runner_tab, "2. Daily Runner")

        # --- Properties Tab ---
        self.properties_tab = PropertiesTab(
            parent=self,
            config_manager=self.config_manager,
            save_properties_callback=lambda: None,
        )
        self.tab_widget.addTab(self.properties_tab, "3. Application Properties")

        # --- View Logs Tab ---
        self.view_logs_tab = ViewLogsTab(
            parent=self,
            load_daily_logs_display_callback=lambda: None,
        )
        self.tab_widget.addTab(self.view_logs_tab, "4. View Daily Logs")

        # Now wire up the real callbacks and cross-tab references
        self._wire_up_tabs()

        # Keyboard shortcuts for Add Phase, Add Epic, Add Task
        self.add_phase_shortcut = QShortcut(QKeySequence("Ctrl+h"), self)
        self.add_phase_shortcut.activated.connect(self._show_add_phase_dialog)
        self.add_epic_shortcut = QShortcut(QKeySequence("Ctrl+j"), self)
        self.add_epic_shortcut.activated.connect(self._show_add_epic_dialog)
        self.add_task_shortcut = QShortcut(QKeySequence("Ctrl+l"), self)
        self.add_task_shortcut.activated.connect(self._show_add_task_dialog)

    def _wire_up_tabs(self) -> None:
        # Project Selection Tab
        self.project_selection_tab.project_combo.currentIndexChanged.disconnect()
        self.project_selection_tab.project_combo.currentIndexChanged.connect(self._on_project_selected)
        self.project_selection_tab.create_project_btn.clicked.disconnect()
        self.project_selection_tab.create_project_btn.clicked.connect(self._create_new_project)
        # Project Setup Tab
        self.project_setup_tab.add_phase_btn.clicked.disconnect()
        self.project_setup_tab.add_phase_btn.clicked.connect(self._show_add_phase_dialog)
        self.project_setup_tab.add_epic_btn.clicked.disconnect()
        self.project_setup_tab.add_epic_btn.clicked.connect(self._show_add_epic_dialog)
        self.project_setup_tab.add_task_btn.clicked.disconnect()
        self.project_setup_tab.add_task_btn.clicked.connect(self._show_add_task_dialog)
        self.project_setup_tab.add_initial_plan_btn.clicked.disconnect()
        self.project_setup_tab.add_initial_plan_btn.clicked.connect(self._add_initial_project_plan)
        # Daily Runner Tab
        self.daily_runner_tab.current_log_date_display.dateChanged.disconnect()
        self.daily_runner_tab.current_log_date_display.dateChanged.connect(self._on_log_date_changed)
        self.daily_runner_tab.simulate_next_day_btn.clicked.disconnect()
        self.daily_runner_tab.simulate_next_day_btn.clicked.connect(self._simulate_next_day)
        self.daily_runner_tab.submit_daily_log_btn.clicked.disconnect()
        self.daily_runner_tab.submit_daily_log_btn.clicked.connect(self._submit_daily_log)
        # Properties Tab
        self.properties_tab.save_properties_btn.clicked.disconnect()
        self.properties_tab.save_properties_btn.clicked.connect(self._save_properties)
        # View Logs Tab
        self.view_logs_tab.log_project_combo.currentIndexChanged.disconnect()
        self.view_logs_tab.log_project_combo.currentIndexChanged.connect(self._load_daily_logs_display)

        # Set up cross-references for shared widgets if needed
        self.project_combo = self.project_selection_tab.project_combo
        self.project_name_input = self.project_selection_tab.project_name_input
        self.project_start_date_input = self.project_selection_tab.project_start_date_input
        self.project_end_date_target_input = self.project_selection_tab.project_end_date_target_input
        self.create_project_btn = self.project_selection_tab.create_project_btn
        self.project_plan_tree = self.project_setup_tab.project_plan_tree
        self.add_phase_btn = self.project_setup_tab.add_phase_btn
        self.add_epic_btn = self.project_setup_tab.add_epic_btn
        self.add_task_btn = self.project_setup_tab.add_task_btn
        self.add_initial_plan_btn = self.project_setup_tab.add_initial_plan_btn
        self.current_project_label = self.daily_runner_tab.current_project_label
        self.current_log_date_display = self.daily_runner_tab.current_log_date_display
        self.simulate_next_day_btn = self.daily_runner_tab.simulate_next_day_btn
        self.activities_us_input = self.daily_runner_tab.activities_us_input
        self.activities_india_input = self.daily_runner_tab.activities_india_input
        self.blockers_us_input = self.daily_runner_tab.blockers_us_input
        self.blockers_india_input = self.daily_runner_tab.blockers_india_input
        self.decisions_made_input = self.daily_runner_tab.decisions_made_input
        self.next_steps_us_input = self.daily_runner_tab.next_steps_us_input
        self.next_steps_india_input = self.daily_runner_tab.next_steps_india_input
        self.submit_daily_log_btn = self.daily_runner_tab.submit_daily_log_btn
        self.property_inputs = self.properties_tab.property_inputs
        self.save_properties_btn = self.properties_tab.save_properties_btn
        self.log_project_combo = self.view_logs_tab.log_project_combo
        self.daily_logs_display = self.view_logs_tab.daily_logs_display

    def _show_add_phase_dialog(self) -> None:
        if self._current_project_id is None:
            QMessageBox.warning(self, "No Project Selected", "Please select a project first.")
            return
        dialog = PhaseDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            phase = self.db_manager.add_phase(
                project_id=self._current_project_id,
                name=data["name"],
                description=data["description"],
                start_date=data["start_date"],
                end_date=data["end_date"]
            )
            # Add to UI tree
            phase_item = QTreeWidgetItem([phase.name, phase.description or "", "", "", ""])
            self.project_plan_tree.addTopLevelItem(phase_item)

    def _show_add_epic_dialog(self) -> None:
        selected_phase_item = self.project_plan_tree.currentItem()
        if selected_phase_item is None: # type: ignore
            if self.project_plan_tree.topLevelItemCount() > 0:
                temp = self.project_plan_tree.topLevelItem(0)
                if temp is not None:
                    selected_phase_item = temp
                    self.project_plan_tree.setCurrentItem(selected_phase_item)
                else:
                    QMessageBox.warning(self, "No Phase Available", "No phases exist. Please add a phase first.")
                    return
            else:
                QMessageBox.warning(self, "No Phase Available", "No phases exist. Please add a phase first.")
                return
        elif selected_phase_item.parent():
            parent = selected_phase_item
            while parent.parent():
                parent = parent.parent()
            selected_phase_item = parent
            self.project_plan_tree.setCurrentItem(selected_phase_item)
        if selected_phase_item is None: # type: ignore
            return
        phase_name = selected_phase_item.text(0)
        phase_id = None
        for project in self.db_manager.get_all_projects():
            for phase in project.phases:
                if phase.name == phase_name:
                    phase_id = phase.id
                    break
        if phase_id is None:
            QMessageBox.warning(self, "Phase Not Found", "Could not find the selected phase in the database.")
            return
        dialog = EpicDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            epic = self.db_manager.add_epic(
                phase_id=phase_id,
                name=data["name"],
                description=data["description"],
                status=data["status"]
            )
            epic_item = QTreeWidgetItem([epic.name, epic.description or "", "", epic.status, ""])
            selected_phase_item.addChild(epic_item)
            selected_phase_item.setExpanded(True)

    def _show_add_task_dialog(self) -> None:
        selected_epic_item = self.project_plan_tree.currentItem()
        if selected_epic_item is None: # type: ignore
            found = False
            for i in range(self.project_plan_tree.topLevelItemCount()):
                phase_item = self.project_plan_tree.topLevelItem(i)
                if phase_item is not None:
                    for j in range(phase_item.childCount()):
                        temp = phase_item.child(j)
                        if temp is not None: # type: ignore
                            selected_epic_item = temp
                            self.project_plan_tree.setCurrentItem(selected_epic_item)
                            found = True
                            break
                if found:
                    break
            if selected_epic_item is None: # type: ignore
                QMessageBox.warning(self, "No Epic Available", "No epics exist. Please add an epic first.")
                return
        elif selected_epic_item.parent() and selected_epic_item.parent().parent():
            while selected_epic_item.parent() and selected_epic_item.parent().parent():
                selected_epic_item = selected_epic_item.parent()
            self.project_plan_tree.setCurrentItem(selected_epic_item)
        if selected_epic_item is None: # type: ignore
            return
        epic_name = selected_epic_item.text(0)
        phase_item = selected_epic_item.parent()
        phase_name = phase_item.text(0) if phase_item else None
        epic_id = None
        for project in self.db_manager.get_all_projects():
            for phase in project.phases:
                if phase.name == phase_name:
                    for epic in phase.epics:
                        if epic.name == epic_name:
                            epic_id = epic.id
                            break
        if epic_id is None:
            QMessageBox.warning(self, "Epic Not Found", "Could not find the selected epic in the database.")
            return
        dialog = TaskDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            task = self.db_manager.add_task(
                epic_id=epic_id,
                name=data["name"],
                description=data["description"],
                assigned_to=data["assigned_to"],
                priority=data["priority"],
                status=data["status"],
                jira_link=data["jira_link"],
                start_date=data["start_date"],
                due_date=data["due_date"]
            )
            task_item = QTreeWidgetItem([
                task.name,
                task.description or "",
                task.assigned_to or "",
                task.status,
                str(task.due_date) if task.due_date else ""
            ])
            selected_epic_item.addChild(task_item)
            selected_epic_item.setExpanded(True)

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


class PhaseDialog(QDialog):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Add Phase")
        self.resize(600, 500)  # M
        layout = QFormLayout(self)
        self.name_input = QLineEdit()
        self.description_input = QLineEdit()
        self.start_date_input = QDateEdit(QDate.currentDate())
        self.start_date_input.setCalendarPopup(True)
        self.end_date_input = QDateEdit(QDate.currentDate())
        self.end_date_input.setCalendarPopup(True)
        layout.addRow("Name:", self.name_input)
        layout.addRow("Description:", self.description_input)
        layout.addRow("Start Date:", self.start_date_input)
        layout.addRow("End Date:", self.end_date_input)
        self.button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        layout.addRow(self.button_box)

    def get_data(self) -> dict[str, Any]:
        return {
            "name": self.name_input.text(),
            "description": self.description_input.text(),
            "start_date": self.start_date_input.date().toPython(),
            "end_date": self.end_date_input.date().toPython(),
        }

class EpicDialog(QDialog):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Add Epic")
        self.resize(600, 500)  # M
        layout = QFormLayout(self)
        self.name_input = QLineEdit()
        self.description_input = QLineEdit()
        self.status_input = QLineEdit("Planned")
        layout.addRow("Name:", self.name_input)
        layout.addRow("Description:", self.description_input)
        layout.addRow("Status:", self.status_input)
        self.button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        layout.addRow(self.button_box)

    def get_data(self) -> dict[str, Any]:
        return {
            "name": self.name_input.text(),
            "description": self.description_input.text(),
            "status": self.status_input.text(),
        }

class TaskDialog(QDialog):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Add Task")
        self.resize(600, 500)  # Make the dialog larger (width, height)
        layout = QFormLayout(self)
        self.name_input = QLineEdit()
        self.description_input = QLineEdit()
        self.assigned_to_input = QLineEdit()
        self.priority_input = QLineEdit("Medium")
        self.status_input = QLineEdit("To Do")
        self.jira_link_input = QLineEdit()
        self.start_date_input = QDateEdit(QDate.currentDate())
        self.start_date_input.setCalendarPopup(True)
        self.due_date_input = QDateEdit(QDate.currentDate())
        self.due_date_input.setCalendarPopup(True)
        layout.addRow("Name:", self.name_input)
        layout.addRow("Description:", self.description_input)
        layout.addRow("Assigned To:", self.assigned_to_input)
        layout.addRow("Priority:", self.priority_input)
        layout.addRow("Status:", self.status_input)
        layout.addRow("Jira Link:", self.jira_link_input)
        layout.addRow("Start Date:", self.start_date_input)
        layout.addRow("Due Date:", self.due_date_input)
        self.button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        layout.addRow(self.button_box)

    def get_data(self) -> dict[str, Any]:
        return {
            "name": self.name_input.text(),
            "description": self.description_input.text(),
            "assigned_to": self.assigned_to_input.text(),
            "priority": self.priority_input.text(),
            "status": self.status_input.text(),
            "jira_link": self.jira_link_input.text(),
            "start_date": self.start_date_input.date().toPython(),
            "due_date": self.due_date_input.date().toPython(),
        }


if __name__ == "__main__":
    # Ensure a QApplication instance exists before creating QWidgets
    app: QApplication = QApplication(sys.argv)
    app.setStyleSheet(qdarktheme.load_stylesheet("light"))
    window: ProjectPlannerApp = ProjectPlannerApp()
    window.show()
    sys.exit(app.exec())


from datetime import timedelta
from database import Phase, Epic
from PySide6.QtWidgets import QMessageBox

def add_initial_project_plan(app) -> None:
    """
    Auto-populates the selected project with a default plan structure
    based on the project description and config settings.
    Expects 'app' to be the ProjectPlannerApp instance.
    """
    if app._current_project_id is None:
        QMessageBox.warning(app, "No Project Selected", "Please select or create a project first.")
        return

    project = app.db_manager.get_project_by_name(app.project_combo.currentText())
    if not project:
        QMessageBox.critical(app, "Error", "Selected project not found in database.")
        return

    reply = QMessageBox.question(app, "Confirm Auto-Populate",
        "This will add a default plan structure (Phases, Epics, Tasks) to the current project. Continue?",
        QMessageBox.Yes | QMessageBox.No)
    if reply == QMessageBox.No:
        return

    try:
        ssa1_name = app.config_manager.get_property('TEAM_MEMBERS', 'SSA1_Name')
        sa2_name = app.config_manager.get_property('TEAM_MEMBERS', 'SA2_Name')
        offshore_pm_name = app.config_manager.get_property('TEAM_MEMBERS', 'Offshore_PM_Name')
        ssa1_name_str = ssa1_name if ssa1_name is not None else "SSA1"
        sa2_name_str = sa2_name if sa2_name is not None else "SA2"
        offshore_pm_name_str = offshore_pm_name if offshore_pm_name is not None else "Offshore PM"

        # Phase 1: Inception & Detailed Planning (Weeks 1-4)
        phase1 = app.db_manager.add_phase(
            project.id,
            "Phase 1: Inception & Detailed Planning (Weeks 1-4)",
            "Establish foundational understanding, detailed requirements, and initial design for key modules.",
            start_date=project.start_date,
            end_date=project.start_date + timedelta(weeks=4)
        )
        epic1_1 = app.db_manager.add_epic(
            phase1.id,
            "Requirements Gathering & Reverse Engineering",
            "Gather business & technical requirements, reverse engineer vendor product."
        )
        app.db_manager.add_task(
            epic1_1.id,
            "Client Kick-off & Expectations Alignment",
            "Formal kick-off with client to align on scope and communication.",
            ssa1_name_str,
            "High",
            due_date=project.start_date + timedelta(days=3),
        )
        app.db_manager.add_task(
            epic1_1.id,
            "Vendor Product Architecture Deep Dive",
            "Dissect existing on-prem MDM product for architecture, APIs, and customization points.",
            f"{ssa1_name_str}, {sa2_name_str}",
            "High",
            due_date=project.start_date + timedelta(days=7),
        )
        app.db_manager.add_task(
            epic1_1.id,
            "Detailed MDM Customization Requirements",
            "Workshops with client BAs for data quality, validations, UI, RBAC.",
            ssa1_name_str,
            "High",
            due_date=project.start_date + timedelta(days=14),
        )
        app.db_manager.add_task(
            epic1_1.id,
            "Ingress Source System Data Mapping (Initial 5)",
            "Detailed data mapping for the first 5 critical ingress sources.",
            sa2_name_str,
            "High",
            due_date=project.start_date + timedelta(days=14),
        )

        epic1_2 = app.db_manager.add_epic(phase1.id, "Technical Design & Initial POCs", "Develop overall architectural design and conduct critical proof of concepts.")
        app.db_manager.add_task(epic1_2.id, "Overall ETL/MDM Solution Architecture", "Design the end-to-end architecture for Ingress, MDM, and Egress.", ssa1_name_str, 'High', due_date=project.start_date + timedelta(days=21))
        app.db_manager.add_task(epic1_2.id, "MDM Customization Framework POC", "Prove out a customization approach for the vendor MDM product.", sa2_name_str, 'High', due_date=project.start_date + timedelta(days=21))
        app.db_manager.add_task(epic1_2.id, "Ingress Data Pipeline POC (Connector)", "Validate connectivity and initial data extraction from a complex source.", sa2_name_str, 'Medium', due_date=project.start_date + timedelta(days=28))
        app.db_manager.add_task(epic1_2.id, "Offshore Team Onboarding & Environment Setup", "Ensure offshore team has access, tools, and dev environments ready.", offshore_pm_name_str, 'High', due_date=project.start_date + timedelta(days=28))

        # Phase 2: Iterative Development & Delivery (Months 2-6)
        phase2 = app.db_manager.add_phase(
            project.id,
            "Phase 2: Iterative Development & Delivery (Months 2-6)",
            "Develop, unit test, and deliver functional modules in iterations.",
            start_date=project.start_date + timedelta(weeks=4),
            end_date=project.start_date + timedelta(weeks=4 + 5*4) # 5 months
        )
        epic2_1 = app.db_manager.add_epic(phase2.id, "Ingress Module Development", "Develop data pipelines for 20 source systems into MDM.")
        app.db_manager.add_task(epic2_1.id, "Ingress Source 1-5 Development & Unit Test", "Develop and unit test pipelines for first 5 critical sources.", offshore_pm_name_str + ' (Offshore Team)', 'High')
        app.db_manager.add_task(epic2_1.id, "Ingress Source 6-10 Development & Unit Test", "Develop and unit test pipelines for next 5 critical sources.", offshore_pm_name_str + ' (Offshore Team)', 'Medium')
        app.db_manager.add_task(epic2_1.id, "Ingress Source 11-20 Development & Unit Test", "Develop and unit test pipelines for remaining sources.", offshore_pm_name_str + ' (Offshore Team)', 'Low')
        app.db_manager.add_task(epic2_1.id, "Ingress Data Quality & Error Handling", "Implement robust data quality checks and error logging for all pipelines.", sa2_name_str, 'High')

        epic2_2 = app.db_manager.add_epic(phase2.id, "Egress Module Development", "Pull data from CRM, identify deltas, and write to CSV files.")
        app.db_manager.add_task(epic2_2.id, "Egress CRM Data Extraction Design", "Design efficient extraction of CRM data.", sa2_name_str, 'High')
        app.db_manager.add_task(epic2_2.id, "Egress Delta Logic Implementation", "Implement logic to identify and process data deltas.", offshore_pm_name_str + ' (Offshore Team)', 'High')
        app.db_manager.add_task(epic2_2.id, "Egress CSV File Generation", "Develop module to generate formatted CSV files.", offshore_pm_name_str + ' (Offshore Team)', 'Medium')

        epic2_3 = app.db_manager.add_epic(phase2.id, "MDM Customization & Configuration", "Implement Data Quality, Validations, UI, RBAC based on requirements.")
        app.db_manager.add_task(epic2_3.id, "MDM Data Quality Rules Implementation", "Implement core data quality rules within MDM.", offshore_pm_name_str + ' (Offshore Team)', 'High')
        app.db_manager.add_task(epic2_3.id, "MDM Data Validation Logic", "Implement custom data validation rules.", offshore_pm_name_str + ' (Offshore Team)', 'High')
        app.db_manager.add_task(epic2_3.id, "MDM UI Customization (Key Screens)", "Customize essential UI screens for data stewardship.", offshore_pm_name_str + ' (Offshore Team)', 'Medium')
        app.db_manager.add_task(epic2_3.id, "MDM RBAC Configuration & Testing", "Configure Role-Based Access Control and test permissions.", sa2_name_str, 'High')
        app.db_manager.add_task(epic2_3.id, "MDM Workflow Customization (if applicable)", "Customize data approval/stewardship workflows.", offshore_pm_name_str + ' (Offshore Team)', 'Medium')

        # Phase 3: UAT & Deployment Readiness (Month 7)
        phase3 = app.db_manager.add_phase(
            project.id,
            "Phase 3: UAT & Deployment Readiness (Month 7)",
            "Achieve client sign-off on functionality, prepare for production deployment.",
            start_date=project.start_date + timedelta(weeks=4 + 5*4),
            end_date=project.end_date_target
        )
        epic3_1 = app.db_manager.add_epic(phase3.id, "User Acceptance Testing (UAT)", "Client-led testing and defect resolution.")
        app.db_manager.add_task(epic3_1.id, "UAT Test Case Review & Preparation", "Work with client BAs to finalize UAT test cases.", ssa1_name_str, 'High')
        app.db_manager.add_task(epic3_1.id, "UAT Environment Setup & Data Load", "Prepare and load data into UAT environment.", sa2_name_str, 'High')
        app.db_manager.add_task(epic3_1.id, "UAT Defect Triage & Resolution Cycles", "Manage, prioritize, and resolve defects found during UAT.", f"{offshore_pm_name_str} (Offshore Team), {ssa1_name_str}", 'High')

        epic3_2 = app.db_manager.add_epic(phase3.id, "Deployment Readiness & Go-Live", "Final preparations for production deployment.")
        app.db_manager.add_task(epic3_2.id, "Production Deployment Plan", "Develop detailed plan including rollback strategy.", ssa1_name_str, 'High')
        app.db_manager.add_task(epic3_2.id, "Pre-Go-Live System Health Checks", "Perform final checks on performance, data integrity.", sa2_name_str, 'High')
        app.db_manager.add_task(epic3_2.id, "Post-Go-Live Support Plan", "Define support structure for immediate post-deployment.", ssa1_name_str, 'High')

        QMessageBox.information(app, "Success", "Initial project plan (Phases, Epics, Tasks) added successfully!")
        app._load_project_plan_tree()
    except Exception as e:
        QMessageBox.critical(app, "Error Adding Plan", f"Failed to add initial plan: {e}")

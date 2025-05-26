# database.py
from sqlalchemy import create_engine, String, Text, Date, DateTime, ForeignKey
from sqlalchemy.orm import (
    sessionmaker,
    declarative_base,
    relationship,
    Session,
    Mapped,
    mapped_column,
)
from datetime import datetime, date
from typing import Optional, List

# Base class for declarative models
Base = declarative_base()


class Project(Base):
    """Represents a main project."""

    __tablename__ = "projects"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    start_date: Mapped[date] = mapped_column(Date, default=date.today)
    end_date_target: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    status: Mapped[str] = mapped_column(
        String, default="Planned"
    )  # Planned, In Progress, Completed, On Hold

    # Relationships
    phases: Mapped[List["Phase"]] = relationship(
        "Phase", back_populates="project", cascade="all, delete-orphan"
    )
    daily_logs: Mapped[List["DailyLog"]] = relationship(
        "DailyLog", back_populates="project", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Project(id={self.id}, name='{self.name}', status='{self.status}')>"


class Phase(Base):
    """Represents a major phase within a project (e.g., Inception, Development)."""

    __tablename__ = "phases"
    id: Mapped[int] = mapped_column(primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"))
    name: Mapped[str] = mapped_column(String, nullable=False)
    start_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    end_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text)

    # Relationships
    project: Mapped["Project"] = relationship("Project", back_populates="phases")
    epics: Mapped[List["Epic"]] = relationship(
        "Epic", back_populates="phase", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Phase(id={self.id}, name='{self.name}')>"


class Epic(Base):
    """Represents a large feature or module within a phase (e.g., Ingress, Egress, MDM Customization)."""

    __tablename__ = "epics"
    id: Mapped[int] = mapped_column(primary_key=True)
    phase_id: Mapped[int] = mapped_column(ForeignKey("phases.id"))
    name: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    status: Mapped[str] = mapped_column(
        String, default="Planned"
    )  # Planned, In Progress, Completed, On Hold

    # Relationships
    phase: Mapped["Phase"] = relationship("Phase", back_populates="epics")
    tasks: Mapped[List["Task"]] = relationship(
        "Task", back_populates="epic", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Epic(id={self.id}, name='{self.name}')>"


class Task(Base):
    """Represents a specific task within an epic."""

    __tablename__ = "tasks"
    id: Mapped[int] = mapped_column(primary_key=True)
    epic_id: Mapped[int] = mapped_column(ForeignKey("epics.id"))
    name: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    assigned_to: Mapped[Optional[str]] = mapped_column(String)
    priority: Mapped[str] = mapped_column(String, default="Medium")  # High, Medium, Low
    status: Mapped[str] = mapped_column(
        String, default="To Do"
    )  # To Do, In Progress, Done, Blocked
    jira_link: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    start_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    due_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    completed_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)

    # Relationships
    epic: Mapped["Epic"] = relationship("Epic", back_populates="tasks")
    subtasks: Mapped[List["SubTask"]] = relationship(
        "SubTask", back_populates="task", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Task(id={self.id}, name='{self.name}', status='{self.status}')>"


class SubTask(Base):
    """Represents a smaller, granular piece of work within a task."""

    __tablename__ = "subtasks"
    id: Mapped[int] = mapped_column(primary_key=True)
    task_id: Mapped[int] = mapped_column(ForeignKey("tasks.id"))
    name: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    assigned_to: Mapped[Optional[str]] = mapped_column(String)
    status: Mapped[str] = mapped_column(
        String, default="To Do"
    )  # To Do, In Progress, Done, Blocked
    completed_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)

    # Relationships
    task: Mapped["Task"] = relationship("Task", back_populates="subtasks")

    def __repr__(self) -> str:
        return f"<SubTask(id={self.id}, name='{self.name}', status='{self.status}')>"


class DailyLog(Base):
    """Stores daily project status updates."""

    __tablename__ = "daily_logs"
    id: Mapped[int] = mapped_column(primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"))
    log_date: Mapped[date] = mapped_column(Date, nullable=False, default=date.today)
    activities_us: Mapped[Optional[str]] = mapped_column(Text)
    activities_india: Mapped[Optional[str]] = mapped_column(Text)
    blockers_us: Mapped[Optional[str]] = mapped_column(Text)
    blockers_india: Mapped[Optional[str]] = mapped_column(Text)
    decisions_made: Mapped[Optional[str]] = mapped_column(Text)
    next_steps_us: Mapped[Optional[str]] = mapped_column(Text)
    next_steps_india: Mapped[Optional[str]] = mapped_column(Text)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)

    # Relationships
    project: Mapped["Project"] = relationship("Project", back_populates="daily_logs")

    def __repr__(self) -> str:
        return f"<DailyLog(id={self.id}, date='{self.log_date}')>"


class ProjectManagerDB:
    """
    Handles all database operations for the project planning application.
    Uses SQLAlchemy for ORM capabilities.
    """

    def __init__(self, db_url: str = "sqlite:///project_plan.db") -> None:
        self.engine = create_engine(db_url)
        # Create all tables defined in Base.metadata if they don't exist
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)

    def get_session(self) -> Session:
        """Returns a new SQLAlchemy session."""
        return self.Session()

    def create_project(self, name: str, start_date: date, end_date_target: date) -> Project:
        """Creates a new project in the database."""
        session: Session = self.get_session()
        project: Project = Project(
            name=name, start_date=start_date, end_date_target=end_date_target
        )
        session.add(project)
        session.commit()
        session.refresh(project)  # Refresh to get the generated ID
        session.close()
        return project

    def get_project_by_name(self, name: str) -> Optional[Project]:
        """Retrieves a project by its name."""
        session: Session = self.get_session()
        project: Optional[Project] = session.query(Project).filter_by(name=name).first()
        session.close()
        return project

    def get_all_projects(self) -> List[Project]:
        """Retrieves all projects from the database."""
        session: Session = self.get_session()
        projects: List[Project] = session.query(Project).all()
        session.close()
        return projects

    def add_phase(
        self,
        project_id: int,
        name: str,
        description: str,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ) -> Phase:
        """Adds a new phase to a project."""
        session: Session = self.get_session()
        phase: Phase = Phase(
            project_id=project_id,
            name=name,
            description=description,
            start_date=start_date,
            end_date=end_date,
        )
        session.add(phase)
        session.commit()
        session.refresh(phase)
        session.close()
        return phase

    def add_epic(self, phase_id: int, name: str, description: str, status: str = "Planned") -> Epic:
        """Adds a new epic to a phase."""
        session: Session = self.get_session()
        epic: Epic = Epic(phase_id=phase_id, name=name, description=description, status=status)
        session.add(epic)
        session.commit()
        session.refresh(epic)
        session.close()
        return epic

    def add_task(
        self,
        epic_id: int,
        name: str,
        description: str,
        assigned_to: str,
        priority: str = "Medium",
        status: str = "To Do",
        jira_link: Optional[str] = None,
        start_date: Optional[date] = None,
        due_date: Optional[date] = None,
    ) -> Task:
        """Adds a new task to an epic."""
        session: Session = self.get_session()
        task: Task = Task(
            epic_id=epic_id,
            name=name,
            description=description,
            assigned_to=assigned_to,
            priority=priority,
            status=status,
            jira_link=jira_link,
            start_date=start_date,
            due_date=due_date,
        )
        session.add(task)
        session.commit()
        session.refresh(task)
        session.close()
        return task

    def update_task_status(self, task_id: int, new_status: str) -> Optional[Task]:
        """Updates the status of a task."""
        session: Session = self.get_session()
        task: Optional[Task] = session.query(Task).get(task_id)
        if task:
            task.status = new_status
            if new_status == "Done":
                task.completed_date = date.today()
            session.commit()
            session.refresh(task)
        session.close()
        return task

    def get_tasks_for_project(self, project_id: int) -> List[Task]:
        """Retrieves all tasks for a given project, including their epic and phase."""
        session: Session = self.get_session()
        tasks: List[Task] = (
            session.query(Task)
            .join(Epic)
            .join(Phase)
            .filter(Phase.project_id == project_id)
            .order_by(Task.due_date.asc(), Task.priority.desc())
            .all()
        )
        session.close()
        return tasks

    def add_daily_log(
        self,
        project_id: int,
        activities_us: str,
        activities_india: str,
        blockers_us: str,
        blockers_india: str,
        decisions_made: str,
        next_steps_us: str,
        next_steps_india: str,
        log_date: Optional[date] = None,
    ) -> DailyLog:
        """Adds a new daily log entry for a project."""
        session: Session = self.get_session()
        log: DailyLog = DailyLog(
            project_id=project_id,
            log_date=log_date if log_date else date.today(),
            activities_us=activities_us,
            activities_india=activities_india,
            blockers_us=blockers_us,
            blockers_india=blockers_india,
            decisions_made=decisions_made,
            next_steps_us=next_steps_us,
            next_steps_india=next_steps_india,
        )
        session.add(log)
        session.commit()
        session.refresh(log)
        session.close()
        return log

    def get_daily_logs_for_project(self, project_id: int) -> List[DailyLog]:
        """Retrieves all daily logs for a given project, ordered by date."""
        session: Session = self.get_session()
        logs: List[DailyLog] = (
            session.query(DailyLog)
            .filter_by(project_id=project_id)
            .order_by(DailyLog.log_date.desc())
            .all()
        )
        session.close()
        return logs

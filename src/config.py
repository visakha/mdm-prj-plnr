# config.py
import configparser
import os
from typing import Optional, List, Tuple, Any


class ConfigManager:
    """
    Manages reading from and writing to the project_config.ini file.
    This file stores dynamic data points like team member names, holidays,
    and default naming conventions for epics/tasks.
    """

    def __init__(self, config_file: str = "project_config.ini") -> None:
        """
        Initializes the ConfigManager.

        Args:
            config_file: The path to the configuration .ini file.
        """
        self.config_file: str = config_file
        self.config: configparser.ConfigParser = configparser.ConfigParser()
        self._load_config()

    def _load_config(self) -> None:
        """
        Loads the configuration from the .ini file.
        Creates a default configuration file if it does not exist.
        """
        if not os.path.exists(self.config_file):
            print(f"Creating default config file: {self.config_file}")
            self._create_default_config()
        self.config.read(self.config_file)

    def _create_default_config(self) -> None:
        """
        Creates a default project_config.ini file with initial settings.
        """
        self.config["PROJECT_DEFAULTS"] = {
            "EpicNameDefault": "Ingress, Egress, MDM Customization",
            "TaskNameDefault": "Requirements Gathering, Technical Design, Development, Testing",
            "SubTaskNameDefault": "Data Mapping, UI Screens, RBAC Roles",
        }
        self.config["TEAM_MEMBERS"] = {
            "SSA1_Name": "Senior Solutions Architect (USA)",
            "SA2_Name": "Solutions Architect (USA)",
            "Offshore_PM_Name": "Offshore Project Manager (India)",
            "Offshore_Devs_Count": "6",
        }
        self.config["HOLIDAYS"] = {
            "India_Holidays_YYYY-MM-DD": "2025-08-15, 2025-10-02, 2025-10-23",  # Example dates: Independence Day, Gandhi Jayanti, Diwali
            "US_Holidays_YYYY-MM-DD": "2025-07-04, 2025-09-01, 2025-11-27",  # Example dates: Independence Day, Labor Day, Thanksgiving
        }
        self.config["SKILLS"] = {
            "SSA1_Skills": "Architecture, MDM, ETL, Client Management, Risk Mitigation",
            "SA2_Skills": "ETL, Data Pipelines, MDM Customization, Hands-on Development, POCs",
            "Offshore_Dev_Skills_Expected": "Python, SQL, ETL Tools, Vendor MDM APIs, Unit Testing",
        }
        self.config["COMMUNICATION"] = {
            "Overlap_Hours": "2",
            "Daily_Call_Time_US_ET": "9:00 AM",
            "Weekly_Recon_Day": "Monday",
            "Weekly_Recon_Time_US_ET": "11:00 AM",
        }
        self.config["PROJECT_CHALLENGES"] = {
            "Time_Constraint": "7 months",
            "Scope_Change_Frequency": "Regular",
            "Team_Technical_Strength": "Not strong, many POCs needed",
            "SSA1_Responsibilities": "Client feedback, design consensus, weekly reporting",
            "SA2_Responsibilities": "Hands-on, technical guidance",
        }
        with open(self.config_file, "w") as f:
            self.config.write(f)

    def get_property(self, section: str, key: str) -> Optional[str]:
        """
        Retrieves a property from the specified section and key.

        Args:
            section: The section name in the .ini file.
            key: The key within the section.

        Returns:
            The string value of the property, or None if not found.
        """
        return self.config.get(section, key, fallback=None)

    def set_property(self, section: str, key: str, value: Any) -> None:
        """
        Sets a property in the specified section and key.
        Creates the section if it doesn't exist.

        Args:
            section: The section name in the .ini file.
            key: The key within the section.
            value: The value to set for the property. Will be converted to string.
        """
        if section not in self.config:
            self.config[section] = {}
        self.config[section][key] = str(value)
        self._save_config()

    def get_section_items(self, section: str) -> List[Tuple[str, str]]:
        """
        Returns all key-value pairs for a given section.

        Args:
            section: The section name in the .ini file.

        Returns:
            A list of tuples, where each tuple contains (key, value) as strings.
            Returns an empty list if the section does not exist.
        """
        if section in self.config:
            return list(self.config.items(section))
        return []

    def _save_config(self) -> None:
        """
        Saves the current configuration back to the .ini file.
        """
        with open(self.config_file, "w") as f:
            self.config.write(f)

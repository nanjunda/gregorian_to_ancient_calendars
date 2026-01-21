from abc import ABC, abstractmethod

class BaseCalendar(ABC):
    """
    Standard interface for all Ancient Calendar Engines.
    This ensures the Hub can communicate with any calendar (Panchanga, Mayan, etc.) 
    using the same protocol.
    """

    @abstractmethod
    def calculate_data(self, date_str, time_str, location_name, lang='EN'):
        """
        Performs the core astronomical/calendar calculations based on input strings.
        Returns a dictionary containing the primary results.
        """
        pass

    @abstractmethod
    def get_visual_configs(self, calculated_data):
        """
        Returns metadata for the 3D visual modules based on the calculation.
        """
        pass

    @abstractmethod
    def get_ai_context(self, calculated_data):
        """
        Returns the data structure formatted for the AI Maestro's prompt.
        """
        pass

    @abstractmethod
    def get_ai_instructions(self):
        """
        Returns the civilization-specific AI prompt/instructions for the context spoke.
        """
        pass

    @abstractmethod
    def generate_ical(self, date_str, time_str, location_name, title, lang):
        """
        Generates iCal (.ics) content for the calendar.
        """
        pass

    @abstractmethod
    def get_rich_visuals(self, date_str, time_str, location_name, title):
        """
        Returns binary/base64 visual data (e.g., SkyMap, Solar System).
        """
        pass

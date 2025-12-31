from ics import Calendar, Event
import pytz

def create_ical_content(title, occurrences):
    """
    Creates iCal content (.ics) for a list of occurrences.
    Each occurrence is a dict with 'datetime' and 'report'.
    """
    c = Calendar()
    
    for occurrence in occurrences:
        e = Event()
        e.name = title
        e.begin = occurrence["datetime"]
        e.duration = {"hours": 1} # Standard 1 hour event
        e.description = occurrence["report"]
        c.events.add(e)
        
    return c.serialize()

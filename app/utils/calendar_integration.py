from icalendar import Calendar, Event
from datetime import datetime
import pytz

def create_ical_event(event_data):
    cal = Calendar()
    cal.add('prodid', '-//Video Hosting SaaS//EN')
    cal.add('version', '2.0')

    event = Event()
    event.add('summary', event_data['title'])
    event.add('description', event_data['description'])
    event.add('dtstart', event_data['start_time'])
    event.add('dtend', event_data['end_time'])
    event.add('dtstamp', datetime.now(pytz.utc))
    event.add('uid', f"{event_data['id']}@videohostingsaas.com")

    cal.add_component(event)
    return cal.to_ical()

def get_google_calendar_url(event_data):
    start = event_data['start_time'].strftime("%Y%m%dT%H%M%SZ")
    end = event_data['end_time'].strftime("%Y%m%dT%H%M%SZ")
    url = f"https://www.google.com/calendar/render?action=TEMPLATE&text={event_data['title']}&dates={start}/{end}&details={event_data['description']}"
    return url

def get_outlook_calendar_url(event_data):
    start = event_data['start_time'].strftime("%Y-%m-%dT%H:%M:%S")
    end = event_data['end_time'].strftime("%Y-%m-%dT%H:%M:%S")
    url = f"https://outlook.live.com/calendar/0/deeplink/compose?subject={event_data['title']}&startdt={start}&enddt={end}&body={event_data['description']}"
    return url

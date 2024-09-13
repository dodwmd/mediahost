from app.notifications.notification_system import create_upcoming_event_notifications
import schedule
import time
import threading

def run_upcoming_event_notifications():
    while True:
        schedule.run_pending()
        time.sleep(1)

def start_notification_scheduler():
    schedule.every().day.at("00:00").do(create_upcoming_event_notifications)
    thread = threading.Thread(target=run_upcoming_event_notifications)
    thread.start()

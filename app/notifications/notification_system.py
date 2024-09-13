from app.database.db import execute_query
from datetime import datetime, timedelta

def create_notification(user_id, message, notification_type, related_id=None):
    query = """
    INSERT INTO notifications (user_id, message, notification_type, related_id, created_at, is_read)
    VALUES (%s, %s, %s, %s, %s, %s)
    """
    params = (user_id, message, notification_type, related_id, datetime.now(), False)
    return execute_query(query, params)

def get_user_notifications(user_id, limit=10):
    query = """
    SELECT * FROM notifications
    WHERE user_id = %s
    ORDER BY created_at DESC
    LIMIT %s
    """
    params = (user_id, limit)
    return execute_query(query, params)

def mark_notification_as_read(notification_id):
    query = """
    UPDATE notifications
    SET is_read = TRUE
    WHERE id = %s
    """
    params = (notification_id,)
    return execute_query(query, params)

def delete_notification(notification_id):
    query = """
    DELETE FROM notifications
    WHERE id = %s
    """
    params = (notification_id,)
    return execute_query(query, params)

def create_event_notification(event_id):
    query = """
    SELECT u.id AS user_id, e.title, e.start_time
    FROM users u
    JOIN events e ON e.content_provider_id = u.id
    WHERE e.id = %s
    """
    params = (event_id,)
    result = execute_query(query, params)
    
    if result:
        event = result[0]
        message = f"New event '{event['title']}' starting on {event['start_time']}"
        create_notification(event['user_id'], message, 'new_event', event_id)

def create_upcoming_event_notifications():
    query = """
    SELECT e.id, e.title, e.start_time, u.id AS user_id
    FROM events e
    JOIN event_access ea ON e.id = ea.event_id
    JOIN users u ON ea.user_id = u.id
    WHERE e.start_time BETWEEN NOW() AND DATE_ADD(NOW(), INTERVAL 1 DAY)
    """
    events = execute_query(query)
    
    for event in events:
        message = f"Reminder: Event '{event['title']}' is starting soon on {event['start_time']}"
        create_notification(event['user_id'], message, 'upcoming_event', event['id'])

def create_new_content_notification(video_id):
    query = """
    SELECT v.title, e.id AS event_id, e.title AS event_title, u.id AS user_id
    FROM videos v
    JOIN events e ON v.event_id = e.id
    JOIN event_access ea ON e.id = ea.event_id
    JOIN users u ON ea.user_id = u.id
    WHERE v.id = %s
    """
    params = (video_id,)
    results = execute_query(query, params)
    
    for result in results:
        message = f"New video '{result['title']}' added to event '{result['event_title']}'"
        create_notification(result['user_id'], message, 'new_content', result['event_id'])

from app.database.db import execute_query
from app.storage.minio_client import upload_file, get_secure_file_url, get_file_url
from app.messaging.nats_client import publish_message
from datetime import datetime, timedelta
import json
import os
from app.auth.auth import require_role
from app.notifications.notification_system import create_event_notification, create_new_content_notification
import pytz

def create_event(content_provider_id, title, description, start_time, end_time, price, categories, tags):
    query = """
    INSERT INTO events (content_provider_id, title, description, start_time, end_time, price, is_published)
    VALUES (%s, %s, %s, %s, %s, %s, %s)
    """
    params = (content_provider_id, title, description, start_time, end_time, price, False)
    event_id = execute_query(query, params)
    
    if event_id:
        for category_id in categories:
            add_event_category(event_id, category_id)
        
        for tag_id in tags:
            add_event_tag(event_id, tag_id)
        
        # Create notification for the new event
        create_event_notification(event_id)
    
    return event_id is not None

def get_events_by_provider(content_provider_id):
    query = """
    SELECT * FROM events WHERE content_provider_id = %s ORDER BY start_time DESC
    """
    params = (content_provider_id,)
    return execute_query(query, params)

@require_role('content_manager')
def update_event(event_id, title, description, start_time, end_time, price, is_published, categories, tags):
    query = """
    UPDATE events
    SET title = %s, description = %s, start_time = %s, end_time = %s, price = %s, is_published = %s
    WHERE id = %s
    """
    params = (title, description, start_time, end_time, price, is_published, event_id)
    result = execute_query(query, params)
    
    if result:
        # Remove existing categories and tags
        execute_query("DELETE FROM event_categories WHERE event_id = %s", (event_id,))
        execute_query("DELETE FROM event_tags WHERE event_id = %s", (event_id,))
        
        # Add new categories and tags
        for category_id in categories:
            add_event_category(event_id, category_id)
        for tag_id in tags:
            add_event_tag(event_id, tag_id)
        
        # Publish message for analytics update
        message = json.dumps({
            "event_id": event_id,
            "action": "update",
            "is_published": is_published
        })
        publish_message("analytics.event_update", message)
    
    return result is not None

@require_role('content_manager')
def delete_event(event_id):
    query = "DELETE FROM events WHERE id = %s"
    params = (event_id,)
    result = execute_query(query, params)
    return result is not None

def add_video_to_event(event_id, title, description, file_data, file_name, duration, qualities=None, subtitles=None):
    file_path = upload_file(file_data, file_name)
    if not file_path:
        return False

    query = """
    INSERT INTO videos (event_id, title, description, file_path, duration, qualities, subtitles)
    VALUES (%s, %s, %s, %s, %s, %s, %s)
    """
    params = (event_id, title, description, file_path, duration, json.dumps(qualities), json.dumps(subtitles))
    result = execute_query(query, params)
    
    if result:
        # Publish message for video processing
        message = json.dumps({
            "video_id": result,
            "file_path": file_path,
            "event_id": event_id,
            "qualities": qualities,
            "subtitles": subtitles
        })
        publish_message("video.processing", message)
        
        # Publish message for email notification
        event = get_event_details(event_id)
        message = json.dumps({
            "event_id": event_id,
            "event_title": event['title'],
            "video_title": title
        })
        publish_message("email.notification", message)
        
        # Create notification for the new content
        create_new_content_notification(result)
    
    return result is not None

def get_videos_by_event(event_id, user_id=None):
    query = "SELECT * FROM videos WHERE event_id = %s"
    params = (event_id,)
    videos = execute_query(query, params)
    
    if videos:
        for video in videos:
            if user_id and has_event_access(user_id, event_id):
                video['url'] = get_secure_file_url(video['file_path'], expires=timedelta(hours=1))
                video['qualities'] = json.loads(video['qualities']) if video['qualities'] else None
                video['subtitles'] = json.loads(video['subtitles']) if video['subtitles'] else None
            else:
                video['url'] = None
                video['qualities'] = None
                video['subtitles'] = None
    
    return videos

def add_merchandise_to_event(event_id, name, description, price, stock_quantity, image_data, image_name):
    image_path = upload_file(image_data, image_name, bucket_name="merchandise")
    if not image_path:
        return False

    query = """
    INSERT INTO merchandise (event_id, name, description, price, stock_quantity, image_path)
    VALUES (%s, %s, %s, %s, %s, %s)
    """
    params = (event_id, name, description, price, stock_quantity, image_path)
    result = execute_query(query, params)
    return result is not None

def update_merchandise(merchandise_id, name, description, price, stock_quantity):
    query = """
    UPDATE merchandise
    SET name = %s, description = %s, price = %s, stock_quantity = %s
    WHERE id = %s
    """
    params = (name, description, price, stock_quantity, merchandise_id)
    result = execute_query(query, params)
    return result is not None

def delete_merchandise(merchandise_id):
    query = "DELETE FROM merchandise WHERE id = %s"
    params = (merchandise_id,)
    result = execute_query(query, params)
    return result is not None

def get_merchandise_by_event(event_id):
    query = "SELECT * FROM merchandise WHERE event_id = %s"
    params = (event_id,)
    merchandise = execute_query(query, params)
    
    if merchandise:
        for item in merchandise:
            item['image_url'] = get_file_url(item['image_path'], bucket_name="merchandise")
    
    return merchandise

def get_merchandise_details(merchandise_id):
    query = "SELECT * FROM merchandise WHERE id = %s"
    params = (merchandise_id,)
    result = execute_query(query, params)
    if result:
        item = result[0]
        item['image_url'] = get_file_url(item['image_path'], bucket_name="merchandise")
        return item
    return None

def get_event_details(event_id, user_id=None):
    query = "SELECT * FROM events WHERE id = %s"
    params = (event_id,)
    event = execute_query(query, params)
    
    if event:
        event = event[0]
        event['start_time'] = pytz.utc.localize(event['start_time'])
        event['end_time'] = pytz.utc.localize(event['end_time'])
        event['videos'] = get_videos_by_event(event_id, user_id)
        event['merchandise'] = get_merchandise_by_event(event_id)
        event['page_blocks'] = get_page_blocks(event_id)
        event['comments'] = get_comments(event_id)
        event['categories'] = get_event_categories(event_id)
        event['tags'] = get_event_tags(event_id)
        if user_id:
            event['user_rating'] = get_user_rating(user_id, event_id)
            # Track the event view
            track_event_view(event_id, user_id)
    
    return event

def get_page_blocks(event_id):
    query = """
    SELECT * FROM page_blocks WHERE event_id = %s ORDER BY order_index
    """
    params = (event_id,)
    return execute_query(query, params)

def has_event_access(user_id, event_id):
    query = """
    SELECT * FROM event_access
    WHERE user_id = %s AND event_id = %s
    """
    params = (user_id, event_id)
    result = execute_query(query, params)
    return len(result) > 0

def get_all_categories():
    query = "SELECT * FROM categories"
    return execute_query(query)

def add_category(name):
    query = "INSERT INTO categories (name) VALUES (%s)"
    params = (name,)
    return execute_query(query, params)

def add_event_category(event_id, category_id):
    query = "INSERT INTO event_categories (event_id, category_id) VALUES (%s, %s)"
    params = (event_id, category_id)
    return execute_query(query, params)

def get_event_categories(event_id):
    query = """
    SELECT c.id, c.name
    FROM categories c
    JOIN event_categories ec ON c.id = ec.category_id
    WHERE ec.event_id = %s
    """
    params = (event_id,)
    return execute_query(query, params)

def remove_event_category(event_id, category_id):
    query = "DELETE FROM event_categories WHERE event_id = %s AND category_id = %s"
    params = (event_id, category_id)
    return execute_query(query, params)

# Add these new functions

def get_all_tags():
    query = "SELECT * FROM tags"
    return execute_query(query)

def add_tag(name):
    query = "INSERT INTO tags (name) VALUES (%s)"
    params = (name,)
    return execute_query(query, params)

def add_event_tag(event_id, tag_id):
    query = "INSERT INTO event_tags (event_id, tag_id) VALUES (%s, %s)"
    params = (event_id, tag_id)
    return execute_query(query, params)

def get_event_tags(event_id):
    query = """
    SELECT t.id, t.name
    FROM tags t
    JOIN event_tags et ON t.id = et.tag_id
    WHERE et.event_id = %s
    """
    params = (event_id,)
    return execute_query(query, params)

def remove_event_tag(event_id, tag_id):
    query = "DELETE FROM event_tags WHERE event_id = %s AND tag_id = %s"
    params = (event_id, tag_id)
    return execute_query(query, params)

# Update the create_event function
def create_event(content_provider_id, title, description, start_time, end_time, price, categories, tags):
    query = """
    INSERT INTO events (content_provider_id, title, description, start_time, end_time, price, is_published)
    VALUES (%s, %s, %s, %s, %s, %s, %s)
    """
    params = (content_provider_id, title, description, start_time, end_time, price, False)
    event_id = execute_query(query, params)
    
    if event_id:
        for category_id in categories:
            add_event_category(event_id, category_id)
        
        for tag_id in tags:
            add_event_tag(event_id, tag_id)
        
        # Create notification for the new event
        create_event_notification(event_id)
    
    return event_id is not None

# Update the update_event function
def update_event(event_id, title, description, start_time, end_time, price, is_published, categories, tags):
    query = """
    UPDATE events
    SET title = %s, description = %s, start_time = %s, end_time = %s, price = %s, is_published = %s
    WHERE id = %s
    """
    params = (title, description, start_time, end_time, price, is_published, event_id)
    result = execute_query(query, params)
    
    if result:
        # Remove existing categories and tags
        execute_query("DELETE FROM event_categories WHERE event_id = %s", (event_id,))
        execute_query("DELETE FROM event_tags WHERE event_id = %s", (event_id,))
        
        # Add new categories and tags
        for category_id in categories:
            add_event_category(event_id, category_id)
        for tag_id in tags:
            add_event_tag(event_id, tag_id)
        
        # Publish message for analytics update
        message = json.dumps({
            "event_id": event_id,
            "action": "update",
            "is_published": is_published
        })
        publish_message("analytics.event_update", message)
    
    return result is not None

# Update the get_event_details function
def get_event_details(event_id, user_id=None):
    query = "SELECT * FROM events WHERE id = %s"
    params = (event_id,)
    event = execute_query(query, params)
    
    if event:
        event = event[0]
        event['start_time'] = pytz.utc.localize(event['start_time'])
        event['end_time'] = pytz.utc.localize(event['end_time'])
        event['videos'] = get_videos_by_event(event_id, user_id)
        event['merchandise'] = get_merchandise_by_event(event_id)
        event['page_blocks'] = get_page_blocks(event_id)
        event['comments'] = get_comments(event_id)
        event['categories'] = get_event_categories(event_id)
        event['tags'] = get_event_tags(event_id)
        if user_id:
            event['user_rating'] = get_user_rating(user_id, event_id)
            # Track the event view
            track_event_view(event_id, user_id)
    
    return event

def add_comment(user_id, event_id, content):
    query = """
    INSERT INTO comments (user_id, event_id, content)
    VALUES (%s, %s, %s)
    """
    params = (user_id, event_id, content)
    return execute_query(query, params)

def get_comments(event_id):
    query = """
    SELECT c.id, c.content, c.created_at, u.username
    FROM comments c
    JOIN users u ON c.user_id = u.id
    WHERE c.event_id = %s
    ORDER BY c.created_at DESC
    """
    params = (event_id,)
    return execute_query(query, params)

def add_rating(user_id, event_id, rating):
    query = """
    INSERT INTO ratings (user_id, event_id, rating)
    VALUES (%s, %s, %s)
    ON DUPLICATE KEY UPDATE rating = VALUES(rating)
    """
    params = (user_id, event_id, rating)
    result = execute_query(query, params)
    
    if result:
        # Update average rating and total ratings for the event
        query = """
        UPDATE events e
        SET average_rating = (SELECT AVG(rating) FROM ratings WHERE event_id = e.id),
            total_ratings = (SELECT COUNT(*) FROM ratings WHERE event_id = e.id)
        WHERE e.id = %s
        """
        execute_query(query, (event_id,))
    
    return result

def get_user_rating(user_id, event_id):
    query = """
    SELECT rating FROM ratings
    WHERE user_id = %s AND event_id = %s
    """
    params = (user_id, event_id)
    result = execute_query(query, params)
    return result[0]['rating'] if result else None

def track_event_view(event_id, user_id):
    query = """
    INSERT INTO event_views (event_id, user_id, timestamp)
    VALUES (%s, %s, NOW())
    """
    params = (event_id, user_id)
    return execute_query(query, params)

def user_has_event_access(user_id, event_id):
    query = """
    SELECT * FROM event_access
    WHERE user_id = %s AND event_id = %s
    """
    params = (user_id, event_id)
    result = execute_query(query, params)
    return len(result) > 0

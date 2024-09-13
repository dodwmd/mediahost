from app.database.db import execute_query
from datetime import datetime

def create_event_feedback(user_id, event_id, rating, comment):
    query = """
    INSERT INTO event_feedback (user_id, event_id, rating, comment, created_at)
    VALUES (%s, %s, %s, %s, %s)
    """
    params = (user_id, event_id, rating, comment, datetime.now())
    return execute_query(query, params)

def create_platform_feedback(user_id, category, rating, comment):
    query = """
    INSERT INTO platform_feedback (user_id, category, rating, comment, created_at)
    VALUES (%s, %s, %s, %s, %s)
    """
    params = (user_id, category, rating, comment, datetime.now())
    return execute_query(query, params)

def get_event_feedback(event_id, limit=5):
    query = """
    SELECT ef.*, u.username
    FROM event_feedback ef
    JOIN users u ON ef.user_id = u.id
    WHERE ef.event_id = %s
    ORDER BY ef.created_at DESC
    LIMIT %s
    """
    params = (event_id, limit)
    return execute_query(query, params)

def get_average_event_rating(event_id):
    query = """
    SELECT AVG(rating) as avg_rating
    FROM event_feedback
    WHERE event_id = %s
    """
    params = (event_id,)
    result = execute_query(query, params)
    return result[0]['avg_rating'] if result else None

def get_platform_feedback(limit=5):
    query = """
    SELECT pf.*, u.username
    FROM platform_feedback pf
    JOIN users u ON pf.user_id = u.id
    ORDER BY pf.created_at DESC
    LIMIT %s
    """
    params = (limit,)
    return execute_query(query, params)

def get_average_platform_rating():
    query = """
    SELECT AVG(rating) as avg_rating
    FROM platform_feedback
    """
    result = execute_query(query)
    return result[0]['avg_rating'] if result else None

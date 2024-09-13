from app.database.db import execute_query
from collections import Counter
import random

def get_user_viewed_events(user_id):
    query = """
    SELECT DISTINCT e.id, e.title, e.description, e.content_provider_id
    FROM events e
    JOIN event_access ea ON e.id = ea.event_id
    WHERE ea.user_id = %s
    """
    params = (user_id,)
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

def get_similar_events(event_id, limit=5):
    categories = get_event_categories(event_id)
    category_ids = [cat['id'] for cat in categories]
    
    query = """
    SELECT DISTINCT e.id, e.title, e.description
    FROM events e
    JOIN event_categories ec ON e.id = ec.event_id
    WHERE ec.category_id IN %s AND e.id != %s AND e.is_published = TRUE
    LIMIT %s
    """
    params = (tuple(category_ids), event_id, limit)
    return execute_query(query, params)

def get_recommended_events(user_id, limit=5):
    viewed_events = get_user_viewed_events(user_id)
    
    if not viewed_events:
        # If the user hasn't viewed any events, return random popular events
        return get_popular_events(limit)
    
    # Count categories and content providers from viewed events
    category_counter = Counter()
    provider_counter = Counter()
    
    for event in viewed_events:
        categories = get_event_categories(event['id'])
        for category in categories:
            category_counter[category['id']] += 1
        provider_counter[event['content_provider_id']] += 1
    
    # Get top categories and providers
    top_categories = [cat for cat, _ in category_counter.most_common(3)]
    top_providers = [prov for prov, _ in provider_counter.most_common(2)]
    
    # Get recommended events based on top categories and providers
    query = """
    SELECT DISTINCT e.id, e.title, e.description
    FROM events e
    JOIN event_categories ec ON e.id = ec.event_id
    WHERE ec.category_id IN %s
    AND e.content_provider_id IN %s
    AND e.id NOT IN %s
    AND e.is_published = TRUE
    LIMIT %s
    """
    viewed_event_ids = tuple(event['id'] for event in viewed_events)
    params = (tuple(top_categories), tuple(top_providers), viewed_event_ids, limit)
    recommended_events = execute_query(query, params)
    
    # If we don't have enough recommendations, add some popular events
    if len(recommended_events) < limit:
        popular_events = get_popular_events(limit - len(recommended_events))
        recommended_events.extend(popular_events)
    
    return recommended_events

def get_popular_events(limit=5):
    query = """
    SELECT e.id, e.title, e.description
    FROM events e
    JOIN event_access ea ON e.id = ea.event_id
    WHERE e.is_published = TRUE
    GROUP BY e.id
    ORDER BY COUNT(ea.id) DESC
    LIMIT %s
    """
    params = (limit,)
    return execute_query(query, params)

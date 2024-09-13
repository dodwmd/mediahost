from app.database.db import execute_query
from datetime import datetime

def advanced_search(
    search_query=None,
    start_date=None,
    end_date=None,
    min_price=None,
    max_price=None,
    categories=None,
    tags=None,
    content_provider=None,
    sort_by='start_time',
    sort_order='ASC',
    page=1,
    per_page=10
):
    query = """
    SELECT DISTINCT e.*, u.username as content_provider_name,
           COALESCE(AVG(r.rating), 0) as avg_rating, 
           COUNT(DISTINCT r.id) as rating_count
    FROM events e
    JOIN users u ON e.content_provider_id = u.id
    LEFT JOIN event_categories ec ON e.id = ec.event_id
    LEFT JOIN event_tags et ON e.id = et.event_id
    LEFT JOIN ratings r ON e.id = r.event_id
    WHERE e.is_published = TRUE
    """
    params = []

    if search_query:
        query += " AND (e.title LIKE %s OR e.description LIKE %s)"
        params.extend([f"%{search_query}%", f"%{search_query}%"])

    if start_date:
        query += " AND e.start_time >= %s"
        params.append(start_date)

    if end_date:
        query += " AND e.end_time <= %s"
        params.append(end_date)

    if min_price is not None:
        query += " AND e.price >= %s"
        params.append(min_price)

    if max_price is not None:
        query += " AND e.price <= %s"
        params.append(max_price)

    if categories:
        query += " AND ec.category_id IN %s"
        params.append(tuple(categories))

    if tags:
        query += " AND et.tag_id IN %s"
        params.append(tuple(tags))

    if content_provider:
        query += " AND u.username LIKE %s"
        params.append(f"%{content_provider}%")

    query += " GROUP BY e.id"

    # Add sorting
    valid_sort_columns = ['start_time', 'price', 'avg_rating', 'rating_count']
    if sort_by in valid_sort_columns:
        query += f" ORDER BY {sort_by} {sort_order}"
    else:
        query += " ORDER BY e.start_time ASC"

    # Add pagination
    offset = (page - 1) * per_page
    query += " LIMIT %s OFFSET %s"
    params.extend([per_page, offset])

    results = execute_query(query, tuple(params))
    
    # Get total count for pagination
    count_query = f"SELECT COUNT(DISTINCT e.id) as total FROM events e WHERE e.is_published = TRUE"
    count_params = []

    if search_query:
        count_query += " AND (e.title LIKE %s OR e.description LIKE %s)"
        count_params.extend([f"%{search_query}%", f"%{search_query}%"])

    if start_date:
        count_query += " AND e.start_time >= %s"
        count_params.append(start_date)

    if end_date:
        count_query += " AND e.end_time <= %s"
        count_params.append(end_date)

    if min_price is not None:
        count_query += " AND e.price >= %s"
        count_params.append(min_price)

    if max_price is not None:
        count_query += " AND e.price <= %s"
        count_params.append(max_price)

    count_result = execute_query(count_query, tuple(count_params))
    total_count = count_result[0]['total'] if count_result else 0

    return results, total_count

def get_categories():
    query = "SELECT * FROM categories"
    result = execute_query(query)
    return result if result else []  # Return an empty list if no categories found

def get_tags():
    query = "SELECT * FROM tags"
    result = execute_query(query)
    return result if result else []  # Return an empty list if no tags found

def get_content_providers():
    query = """
    SELECT DISTINCT u.username
    FROM users u
    JOIN events e ON u.id = e.content_provider_id
    WHERE e.is_published = TRUE
    """
    return execute_query(query)

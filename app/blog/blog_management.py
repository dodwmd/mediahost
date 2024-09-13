from app.database.db import execute_query
from datetime import datetime

def create_blog_post(author_id, title, content, is_published=False):
    query = """
    INSERT INTO blog_posts (author_id, title, content, is_published, created_at, updated_at)
    VALUES (%s, %s, %s, %s, %s, %s)
    """
    params = (author_id, title, content, is_published, datetime.now(), datetime.now())
    return execute_query(query, params)

def get_blog_posts(limit=5):
    query = """
    SELECT b.*, u.username as author_name
    FROM blog_posts b
    JOIN users u ON b.author_id = u.id
    WHERE b.is_published = TRUE
    ORDER BY b.created_at DESC
    LIMIT %s
    """
    result = execute_query(query, (limit,))
    return result if result else []  # Return an empty list if no posts found

def get_blog_post(post_id):
    query = """
    SELECT bp.*, u.username as author_name
    FROM blog_posts bp
    JOIN users u ON bp.author_id = u.id
    WHERE bp.id = %s
    """
    params = (post_id,)
    result = execute_query(query, params)
    return result[0] if result else None

def update_blog_post(post_id, title, content, is_published):
    query = """
    UPDATE blog_posts
    SET title = %s, content = %s, is_published = %s, updated_at = %s
    WHERE id = %s
    """
    params = (title, content, is_published, datetime.now(), post_id)
    return execute_query(query, params)

def delete_blog_post(post_id):
    query = "DELETE FROM blog_posts WHERE id = %s"
    params = (post_id,)
    return execute_query(query, params)

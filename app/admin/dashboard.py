import streamlit as st
from app.database.db import execute_query
from app.auth.auth import require_role
import pandas as pd
import plotly.express as px

@require_role('admin')
def admin_dashboard():
    st.title("Admin Dashboard")

    # Overview metrics
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Users", get_total_users())
    col2.metric("Total Events", get_total_events())
    col3.metric("Total Revenue", f"${get_total_revenue():.2f}")
    col4.metric("Active Subscriptions", get_active_subscriptions())

    # User growth chart
    st.subheader("User Growth")
    user_growth_data = get_user_growth_data()
    fig = px.line(user_growth_data, x='date', y='total_users', title='User Growth Over Time')
    st.plotly_chart(fig)

    # Event distribution chart
    st.subheader("Event Distribution")
    event_distribution = get_event_distribution()
    fig = px.pie(event_distribution, values='count', names='category', title='Event Distribution by Category')
    st.plotly_chart(fig)

    # Recent activities
    st.subheader("Recent Activities")
    activities = get_recent_activities()
    for activity in activities:
        st.write(f"{activity['timestamp']} - {activity['description']}")

    # System health
    st.subheader("System Health")
    system_health = get_system_health()
    st.write(f"CPU Usage: {system_health['cpu_usage']}%")
    st.write(f"Memory Usage: {system_health['memory_usage']}%")
    st.write(f"Disk Usage: {system_health['disk_usage']}%")

def get_total_users():
    query = "SELECT COUNT(*) as count FROM users"
    result = execute_query(query)
    return result[0]['count']

def get_total_events():
    query = "SELECT COUNT(*) as count FROM events"
    result = execute_query(query)
    return result[0]['count']

def get_total_revenue():
    query = "SELECT SUM(price) as total FROM event_access"
    result = execute_query(query)
    return result[0]['total'] or 0

def get_active_subscriptions():
    query = "SELECT COUNT(*) as count FROM subscriptions WHERE status = 'active'"
    result = execute_query(query)
    return result[0]['count']

def get_user_growth_data():
    query = """
    SELECT DATE(created_at) as date, COUNT(*) as total_users
    FROM users
    GROUP BY DATE(created_at)
    ORDER BY date
    """
    return pd.DataFrame(execute_query(query))

def get_event_distribution():
    query = """
    SELECT c.name as category, COUNT(*) as count
    FROM events e
    JOIN event_categories ec ON e.id = ec.event_id
    JOIN categories c ON ec.category_id = c.id
    GROUP BY c.name
    """
    return pd.DataFrame(execute_query(query))

def get_recent_activities():
    query = """
    SELECT 'New User' as type, username as description, created_at as timestamp
    FROM users
    UNION ALL
    SELECT 'New Event' as type, title as description, created_at as timestamp
    FROM events
    ORDER BY timestamp DESC
    LIMIT 10
    """
    return execute_query(query)

def get_system_health():
    # This is a placeholder. In a real-world scenario, you'd use a library like psutil
    # to get actual system metrics.
    return {
        "cpu_usage": 45,
        "memory_usage": 60,
        "disk_usage": 55
    }

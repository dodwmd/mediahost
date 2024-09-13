import streamlit as st
import pandas as pd
import plotly.express as px
from app.database.db import execute_query
from app.auth.auth import require_role

@require_role('content_manager')
def analytics_dashboard(user_id):
    st.title("Content Provider Analytics Dashboard")

    # Get all events for the content provider
    events = get_provider_events(user_id)
    
    if not events:
        st.warning("You don't have any events yet. Create an event to see analytics.")
        return

    # Event selector
    event_options = {event['title']: event['id'] for event in events}
    selected_event = st.selectbox("Select Event", list(event_options.keys()))
    event_id = event_options[selected_event]

    # Date range selector
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("Start Date")
    with col2:
        end_date = st.date_input("End Date")

    # Fetch analytics data
    views_data = get_event_views(event_id, start_date, end_date)
    engagement_data = get_event_engagement(event_id, start_date, end_date)
    revenue_data = get_event_revenue(event_id, start_date, end_date)

    # Display analytics
    display_views_analytics(views_data)
    display_engagement_analytics(engagement_data)
    display_revenue_analytics(revenue_data)

def get_provider_events(user_id):
    query = """
    SELECT id, title FROM events WHERE content_provider_id = %s
    """
    return execute_query(query, (user_id,))

def get_event_views(event_id, start_date, end_date):
    query = """
    SELECT DATE(timestamp) as date, COUNT(*) as views
    FROM event_views
    WHERE event_id = %s AND timestamp BETWEEN %s AND %s
    GROUP BY DATE(timestamp)
    ORDER BY date
    """
    return execute_query(query, (event_id, start_date, end_date))

def get_event_engagement(event_id, start_date, end_date):
    query = """
    SELECT 
        DATE(c.created_at) as date,
        COUNT(DISTINCT c.id) as comments,
        COUNT(DISTINCT r.id) as ratings,
        AVG(r.rating) as avg_rating
    FROM events e
    LEFT JOIN comments c ON e.id = c.event_id AND c.created_at BETWEEN %s AND %s
    LEFT JOIN ratings r ON e.id = r.event_id AND r.created_at BETWEEN %s AND %s
    WHERE e.id = %s
    GROUP BY DATE(c.created_at)
    ORDER BY date
    """
    return execute_query(query, (start_date, end_date, start_date, end_date, event_id))

def get_event_revenue(event_id, start_date, end_date):
    query = """
    SELECT DATE(ea.access_granted_at) as date, COUNT(*) as purchases, SUM(e.price) as revenue
    FROM event_access ea
    JOIN events e ON ea.event_id = e.id
    WHERE ea.event_id = %s AND ea.access_granted_at BETWEEN %s AND %s
    GROUP BY DATE(ea.access_granted_at)
    ORDER BY date
    """
    return execute_query(query, (event_id, start_date, end_date))

def display_views_analytics(views_data):
    st.subheader("Views Analytics")
    if views_data:
        df = pd.DataFrame(views_data)
        fig = px.line(df, x='date', y='views', title='Daily Views')
        st.plotly_chart(fig)
        st.write(f"Total Views: {df['views'].sum()}")
    else:
        st.write("No view data available for the selected period.")

def display_engagement_analytics(engagement_data):
    st.subheader("Engagement Analytics")
    if engagement_data:
        df = pd.DataFrame(engagement_data)
        fig = px.line(df, x='date', y=['comments', 'ratings'], title='Daily Engagement')
        st.plotly_chart(fig)
        
        avg_rating = df['avg_rating'].mean()
        st.write(f"Average Rating: {avg_rating:.2f}")
        st.write(f"Total Comments: {df['comments'].sum()}")
        st.write(f"Total Ratings: {df['ratings'].sum()}")
    else:
        st.write("No engagement data available for the selected period.")

def display_revenue_analytics(revenue_data):
    st.subheader("Revenue Analytics")
    if revenue_data:
        df = pd.DataFrame(revenue_data)
        fig = px.line(df, x='date', y='revenue', title='Daily Revenue')
        st.plotly_chart(fig)
        st.write(f"Total Revenue: ${df['revenue'].sum():.2f}")
        st.write(f"Total Purchases: {df['purchases'].sum()}")
    else:
        st.write("No revenue data available for the selected period.")

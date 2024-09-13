import streamlit as st
import pandas as pd
import plotly.express as px
from app.database.db import execute_query
from app.auth.auth import require_role
import os
from dotenv import load_dotenv
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from datetime import datetime, timedelta

load_dotenv()

# Set up Google Analytics credentials
SCOPES = ['https://www.googleapis.com/auth/analytics.readonly']
KEY_FILE_LOCATION = os.getenv('GOOGLE_ANALYTICS_KEY_FILE')
VIEW_ID = os.getenv('GOOGLE_ANALYTICS_VIEW_ID')

def initialize_analyticsreporting():
    credentials = Credentials.from_authorized_user_file(KEY_FILE_LOCATION, SCOPES)
    analytics = build('analyticsreporting', 'v4', credentials=credentials)
    return analytics

def get_report(analytics, start_date, end_date):
    return analytics.reports().batchGet(
        body={
            'reportRequests': [
                {
                    'viewId': VIEW_ID,
                    'dateRanges': [{'startDate': start_date, 'endDate': end_date}],
                    'metrics': [{'expression': 'ga:sessions'}, {'expression': 'ga:pageviews'}],
                    'dimensions': [{'name': 'ga:date'}]
                }
            ]
        }
    ).execute()

def parse_response(response):
    report = response['reports'][0]
    rows = report['data']['rows']
    
    data = []
    for row in rows:
        data.append({
            'date': datetime.strptime(row['dimensions'][0], '%Y%m%d').date(),
            'sessions': int(row['metrics'][0]['values'][0]),
            'pageviews': int(row['metrics'][0]['values'][1])
        })
    
    return pd.DataFrame(data)

@require_role(['admin', 'content_manager'])
def advanced_analytics_dashboard(user_id, user_role):
    st.title("Advanced Analytics Dashboard")

    # Date range selector
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("Start Date", value=datetime.now() - timedelta(days=30))
    with col2:
        end_date = st.date_input("End Date", value=datetime.now())

    # Google Analytics data
    analytics = initialize_analyticsreporting()
    response = get_report(analytics, start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'))
    ga_data = parse_response(response)

    # Display Google Analytics data
    st.subheader("Google Analytics Overview")
    fig = px.line(ga_data, x='date', y=['sessions', 'pageviews'], title='Sessions and Pageviews')
    st.plotly_chart(fig)

    # Custom analytics for content providers
    if user_role == 'content_manager':
        display_content_provider_analytics(user_id, start_date, end_date)
    
    # Platform-wide analytics for admins
    if user_role == 'admin':
        display_admin_analytics(start_date, end_date)

def display_content_provider_analytics(user_id, start_date, end_date):
    st.subheader("Your Content Performance")

    # Event performance
    event_performance = get_event_performance(user_id, start_date, end_date)
    if not event_performance.empty:
        fig = px.bar(event_performance, x='event_title', y=['views', 'purchases'], title='Event Performance')
        st.plotly_chart(fig)
    else:
        st.write("No event data available for the selected period.")

    # Revenue analysis
    revenue_data = get_revenue_data(user_id, start_date, end_date)
    if not revenue_data.empty:
        fig = px.line(revenue_data, x='date', y='revenue', title='Daily Revenue')
        st.plotly_chart(fig)
        st.write(f"Total Revenue: ${revenue_data['revenue'].sum():.2f}")
    else:
        st.write("No revenue data available for the selected period.")

    # User engagement
    user_engagement = get_user_engagement(user_id, start_date, end_date)
    if not user_engagement.empty:
        fig = px.scatter(user_engagement, x='avg_view_duration', y='engagement_rate', 
                         size='total_views', hover_name='event_title', 
                         title='User Engagement by Event')
        st.plotly_chart(fig)
    else:
        st.write("No user engagement data available for the selected period.")

def display_admin_analytics(start_date, end_date):
    st.subheader("Platform-wide Analytics")

    # User growth
    user_growth = get_user_growth(start_date, end_date)
    if not user_growth.empty:
        fig = px.line(user_growth, x='date', y=['total_users', 'new_users'], title='User Growth')
        st.plotly_chart(fig)
    else:
        st.write("No user growth data available for the selected period.")

    # Content provider performance
    provider_performance = get_provider_performance(start_date, end_date)
    if not provider_performance.empty:
        fig = px.scatter(provider_performance, x='total_events', y='total_revenue', 
                         size='total_views', hover_name='provider_name', 
                         title='Content Provider Performance')
        st.plotly_chart(fig)
    else:
        st.write("No content provider performance data available for the selected period.")

    # Platform revenue
    platform_revenue = get_platform_revenue(start_date, end_date)
    if not platform_revenue.empty:
        fig = px.line(platform_revenue, x='date', y='revenue', title='Platform Daily Revenue')
        st.plotly_chart(fig)
        st.write(f"Total Platform Revenue: ${platform_revenue['revenue'].sum():.2f}")
    else:
        st.write("No platform revenue data available for the selected period.")

# Helper functions to fetch data for analytics
def get_event_performance(user_id, start_date, end_date):
    query = """
    SELECT e.title as event_title, 
           COUNT(DISTINCT ev.id) as views, 
           COUNT(DISTINCT ea.id) as purchases
    FROM events e
    LEFT JOIN event_views ev ON e.id = ev.event_id AND ev.timestamp BETWEEN %s AND %s
    LEFT JOIN event_access ea ON e.id = ea.event_id AND ea.access_granted_at BETWEEN %s AND %s
    WHERE e.content_provider_id = %s
    GROUP BY e.id
    """
    result = execute_query(query, (start_date, end_date, start_date, end_date, user_id))
    return pd.DataFrame(result)

def get_revenue_data(user_id, start_date, end_date):
    query = """
    SELECT DATE(ea.access_granted_at) as date, SUM(e.price) as revenue
    FROM event_access ea
    JOIN events e ON ea.event_id = e.id
    WHERE e.content_provider_id = %s AND ea.access_granted_at BETWEEN %s AND %s
    GROUP BY DATE(ea.access_granted_at)
    """
    result = execute_query(query, (user_id, start_date, end_date))
    return pd.DataFrame(result)

def get_user_engagement(user_id, start_date, end_date):
    query = """
    SELECT e.title as event_title, 
           AVG(TIMESTAMPDIFF(SECOND, ev.timestamp, ev.end_timestamp)) as avg_view_duration,
           COUNT(DISTINCT ev.user_id) / COUNT(DISTINCT ea.user_id) as engagement_rate,
           COUNT(DISTINCT ev.id) as total_views
    FROM events e
    LEFT JOIN event_views ev ON e.id = ev.event_id AND ev.timestamp BETWEEN %s AND %s
    LEFT JOIN event_access ea ON e.id = ea.event_id AND ea.access_granted_at <= %s
    WHERE e.content_provider_id = %s
    GROUP BY e.id
    """
    result = execute_query(query, (start_date, end_date, end_date, user_id))
    return pd.DataFrame(result)

def get_user_growth(start_date, end_date):
    query = """
    SELECT DATE(created_at) as date, 
           COUNT(*) as new_users,
           (SELECT COUNT(*) FROM users WHERE created_at <= DATE(u.created_at)) as total_users
    FROM users u
    WHERE created_at BETWEEN %s AND %s
    GROUP BY DATE(created_at)
    """
    result = execute_query(query, (start_date, end_date))
    return pd.DataFrame(result)

def get_provider_performance(start_date, end_date):
    query = """
    SELECT u.username as provider_name,
           COUNT(DISTINCT e.id) as total_events,
           SUM(e.price * ea.id) as total_revenue,
           COUNT(DISTINCT ev.id) as total_views
    FROM users u
    JOIN events e ON u.id = e.content_provider_id
    LEFT JOIN event_access ea ON e.id = ea.event_id AND ea.access_granted_at BETWEEN %s AND %s
    LEFT JOIN event_views ev ON e.id = ev.event_id AND ev.timestamp BETWEEN %s AND %s
    WHERE u.is_content_provider = TRUE
    GROUP BY u.id
    """
    result = execute_query(query, (start_date, end_date, start_date, end_date))
    return pd.DataFrame(result)

def get_platform_revenue(start_date, end_date):
    query = """
    SELECT DATE(ea.access_granted_at) as date, SUM(e.price) as revenue
    FROM event_access ea
    JOIN events e ON ea.event_id = e.id
    WHERE ea.access_granted_at BETWEEN %s AND %s
    GROUP BY DATE(ea.access_granted_at)
    """
    result = execute_query(query, (start_date, end_date))
    return pd.DataFrame(result)

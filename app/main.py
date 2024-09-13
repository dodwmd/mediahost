import streamlit as st
import os
from dotenv import load_dotenv
from auth.auth import register_user, login_user, get_user_profile, update_user_profile, require_role
from auth.forms import registration_form, login_form, profile_form
from events.event_management import (
    create_event, get_events_by_provider, update_event, delete_event,
    add_video_to_event, get_videos_by_event,
    add_merchandise_to_event, get_merchandise_by_event, update_merchandise, delete_merchandise,
    get_event_details, get_merchandise_details,
    get_all_categories, add_category, add_event_category, get_event_categories, remove_event_category,
    get_all_tags, add_tag, add_event_tag, get_event_tags, remove_event_tag
)
from landing_page.builder import landing_page_builder
from landing_page.display import display_landing_page
from events.event_browser import event_browser
from payments.stripe_integration import create_checkout_session, handle_successful_payment, has_event_access, create_merchandise_checkout_session, handle_successful_merchandise_payment
from messaging.nats_client import initialize_nats
from utils.theme_manager import initialize_theme
from recommendations.recommendation_engine import get_recommended_events
from analytics.dashboard import analytics_dashboard
from notifications.notification_system import get_user_notifications, mark_notification_as_read, delete_notification
from tasks.notification_tasks import start_notification_scheduler
from user.dashboard import user_dashboard
from datetime import datetime, timedelta
import asyncio
import logging
from prometheus_client import Counter, Histogram, CollectorRegistry, generate_latest
import time
from utils.custom_css import get_custom_css
from content.faq import get_faq_content
from blog.blog_management import get_blog_posts, get_blog_post, create_blog_post, update_blog_post, delete_blog_post
from analytics.advanced_analytics import advanced_analytics_dashboard
from utils.seo_utils import generate_seo_friendly_url
from utils.sitemap_generator import generate_sitemap
from feedback.platform_feedback import platform_feedback_page
from admin.dashboard import admin_dashboard
from app.api_docs import api_documentation

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Set up Prometheus metrics
REGISTRY = CollectorRegistry()
REQUEST_COUNT = Counter('request_count', 'App Request Count', ['method', 'endpoint'], registry=REGISTRY)
REQUEST_LATENCY = Histogram('request_latency_seconds', 'Request latency in seconds', ['method', 'endpoint'], registry=REGISTRY)

# Initialize NATS
asyncio.run(initialize_nats())

# Start the notification scheduler
start_notification_scheduler()

load_dotenv()

def main():
    # Set page config first
    st.set_page_config(layout="wide")

    start_time = time.time()
    
    initialize_theme()

    # Get the base URL for sharing
    base_url = os.getenv('DOMAIN_NAME', 'mediahost.dodwell.us')

    # Set the site name
    site_name = os.getenv('SITE_NAME', 'MediaHost')
    st.title(site_name)
    
    st.markdown(get_custom_css(), unsafe_allow_html=True)

    # Check if the request is for metrics
    if "metrics" in st.query_params:
        st.text(generate_latest(REGISTRY).decode())
        return

    st.sidebar.title("Video Hosting SaaS")

    menu = ["Home", "Event Browser", "Login", "Register", "Profile", "Content Provider Dashboard", "View Event", "Purchase Success", "Merchandise Success", "Recommendations", "Advanced Search", "User Dashboard", "FAQ", "Blog", "Advanced Analytics", "Platform Feedback", "Admin Dashboard", "API Documentation"]
    choice = st.sidebar.selectbox("Menu", menu)

    # Log the user's choice
    logger.info(f"User selected menu item: {choice}")

    # Update Prometheus metrics
    REQUEST_COUNT.labels(method='GET', endpoint=choice).inc()

    if choice == "Home":
        st.header("Welcome to Video Hosting SaaS")
        st.write("Please use the Event Browser to discover events or login to access more features.")

    elif choice == "Event Browser":
        event_browser()

    elif choice == "Login":
        st.header("Login")
        login_data = login_form()
        if login_data:
            result = login_user(login_data['username'], login_data['password'])
            if result:
                st.success("Logged in successfully")
                st.session_state['user'] = result['user']
                st.rerun()
            else:
                st.error("Invalid username or password")

    elif choice == "Register":
        st.header("Create New Account")
        reg_data = registration_form()
        if reg_data:
            if register_user(reg_data['username'], reg_data['email'], reg_data['password'], reg_data['is_content_provider']):
                st.success("Registration Successful")
                st.info("Please login to continue")
            else:
                st.error("Registration Failed. Please check the logs for more information.")
                logger.error(f"Registration failed for user: {reg_data['username']}")

    elif choice == "Profile":
        if 'user' in st.session_state:
            st.header("User Profile")
            user = get_user_profile(st.session_state['user']['username'])
            if user:
                st.write(f"Username: {user['username']}")
                st.write(f"Email: {user['email']}")
                st.write(f"Account Type: {'Content Provider' if user['is_content_provider'] else 'Regular User'}")
                st.write(f"Created At: {user['created_at']}")

                st.subheader("Update Profile")
                update_data = profile_form(user)
                if update_data:
                    if update_user_profile(user['username'], update_data['email']):
                        st.success("Profile updated successfully")
                        st.rerun()
                    else:
                        st.error("Failed to update profile")

                if st.button("Logout"):
                    del st.session_state['user']
                    st.rerun()
            else:
                st.error("Failed to fetch user profile")
        else:
            st.warning("Please login to view your profile")

    elif choice == "Content Provider Dashboard":
        if 'user' in st.session_state:
            user_role = st.session_state['user'].get('role')
            if user_role in ['admin', 'content_manager']:
                content_provider_dashboard()
            else:
                st.warning("You don't have permission to access this page.")
        else:
            st.warning("Please log in to access this page.")

    elif choice == "View Event":
        event_id = st.session_state.get('view_event_id')
        if event_id:
            event = get_event_details(event_id)
            if event:
                seo_friendly_url = generate_seo_friendly_url(event['title'])
                # Update the URL without using the deprecated function
                st.query_params["event"] = seo_friendly_url
            display_landing_page(event_id)
        else:
            st.warning("Please select an event to view.")

    elif choice == "Purchase Success":
        session_id = st.query_params.get("session_id")
        if session_id:
            if handle_successful_payment(session_id[0]):
                st.success("Payment successful! You now have access to the event.")
            else:
                st.error("Failed to process payment. Please contact support.")
        else:
            st.warning("Invalid session ID.")

    elif choice == "Merchandise Success":
        session_id = st.query_params.get("session_id")
        if session_id:
            if handle_successful_merchandise_payment(session_id[0]):
                st.success("Payment successful! Your merchandise purchase has been recorded.")
            else:
                st.error("Failed to process merchandise payment. Please contact support.")
        else:
            st.warning("Invalid session ID.")

    elif choice == "Recommendations":
        if 'user' in st.session_state:
            display_recommendations()
        else:
            st.warning("Please log in to view personalized recommendations.")

    elif choice == "Advanced Search":
        event_browser()

    elif choice == "User Dashboard":
        if 'user' in st.session_state:
            user_dashboard(st.session_state['user']['id'])
        else:
            st.warning("Please log in to view your dashboard.")

    elif choice == "FAQ":
        display_faq()

    elif choice == "Blog":
        display_blog()

    elif choice == "Advanced Analytics":
        if 'user' in st.session_state and st.session_state['user']['role'] in ['admin', 'content_manager']:
            advanced_analytics_dashboard(st.session_state['user']['id'], st.session_state['user']['role'])
        else:
            st.warning("You don't have permission to access this page.")

    elif choice == "Platform Feedback":
        platform_feedback_page()

    elif choice == "Admin Dashboard":
        if 'user' in st.session_state and st.session_state['user']['role'] == 'admin':
            admin_dashboard()
        else:
            st.warning("You don't have permission to access this page.")

    elif choice == "API Documentation":
        api_documentation()

    # Calculate request latency and update Prometheus metric
    latency = time.time() - start_time
    REQUEST_LATENCY.labels(method='GET', endpoint=choice).observe(latency)

    # Add a notifications section in the sidebar
    if 'user' in st.session_state:
        user_data = st.session_state['user']
        with st.sidebar.expander("User Info"):
            st.write(f"Username: {user_data.get('username')}")
            st.write(f"Role: {user_data.get('role', 'Unknown')}")
        
        with st.sidebar.expander("Notifications"):
            notifications = get_user_notifications(user_data.get('id'))
            if notifications:
                for notif in notifications:
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.write(notif['message'])
                    with col2:
                        if st.button("Mark as Read", key=f"read_{notif['id']}"):
                            mark_notification_as_read(notif['id'])
                            st.rerun()
                        if st.button("Delete", key=f"delete_{notif['id']}"):
                            delete_notification(notif['id'])
                            st.rerun()
            else:
                st.write("No new notifications")

def display_faq():
    st.title("Frequently Asked Questions")
    faq_content = get_faq_content()
    if isinstance(faq_content, list):
        for item in faq_content:
            with st.expander(item['question']):
                st.write(item['answer'])
    elif isinstance(faq_content, dict):
        for question, answer in faq_content.items():
            with st.expander(question):
                st.write(answer)
    else:
        st.error("FAQ content is in an unexpected format.")

def display_blog():
    st.title("Blog")

    # Display latest blog posts
    posts = get_blog_posts(limit=5)
    if posts:
        for post in posts:
            with st.expander(f"{post['title']} - by {post['author_name']} on {post['created_at']}"):
                st.write(post['content'][:200] + "...")  # Display a preview of the content
                if st.button(f"Read More", key=f"read_more_{post['id']}"):
                    st.session_state['view_post_id'] = post['id']
                    st.rerun()
    else:
        st.write("No blog posts available at the moment.")

    # View full blog post
    if 'view_post_id' in st.session_state:
        post = get_blog_post(st.session_state['view_post_id'])
        if post:
            st.title(post['title'])
            st.write(f"By {post['author_name']} on {post['created_at']}")
            st.write(post['content'])
            if st.button("Back to Blog List"):
                del st.session_state['view_post_id']
                st.rerun()
        else:
            st.error("Blog post not found.")

def display_recommendations():
    st.title("Recommended Events")
    user_id = st.session_state['user']['id']
    recommended_events = get_recommended_events(user_id)
    
    if not recommended_events:
        st.write("No recommendations available at the moment. Try exploring more events!")
    else:
        for event in recommended_events:
            with st.expander(f"{event['title']} - {event['start_time']}"):
                st.write(f"Description: {event['description']}")
                st.write(f"Start: {event['start_time']}")
                st.write(f"End: {event['end_time']}")
                st.write(f"Price: ${event['price']}")
                if st.button(f"View Event", key=f"view_event_{event['id']}"):
                    st.session_state['view_event_id'] = event['id']
                    st.rerun()

if __name__ == "__main__":
    main()

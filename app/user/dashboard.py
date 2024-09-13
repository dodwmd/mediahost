import streamlit as st
from app.database.db import execute_query
from app.recommendations.recommendation_engine import get_recommended_events
from datetime import datetime

def get_user_purchased_events(user_id):
    query = """
    SELECT e.*, ea.access_granted_at
    FROM events e
    JOIN event_access ea ON e.id = ea.event_id
    WHERE ea.user_id = %s
    ORDER BY e.start_time DESC
    """
    params = (user_id,)
    return execute_query(query, params)

def get_user_upcoming_events(user_id):
    query = """
    SELECT e.*
    FROM events e
    JOIN event_access ea ON e.id = ea.event_id
    WHERE ea.user_id = %s AND e.start_time > NOW()
    ORDER BY e.start_time ASC
    """
    params = (user_id,)
    return execute_query(query, params)

def user_dashboard(user_id):
    st.title("Your Dashboard")

    # Purchased Events
    st.header("Your Purchased Events")
    purchased_events = get_user_purchased_events(user_id)
    if purchased_events:
        for event in purchased_events:
            with st.expander(f"{event['title']} - {event['start_time']}"):
                st.write(f"Description: {event['description']}")
                st.write(f"Start: {event['start_time']}")
                st.write(f"End: {event['end_time']}")
                st.write(f"Access Granted: {event['access_granted_at']}")
                if st.button(f"View Event {event['id']}", key=f"view_purchased_{event['id']}"):
                    st.session_state['view_event_id'] = event['id']
                    st.experimental_rerun()
    else:
        st.write("You haven't purchased any events yet.")

    # Upcoming Events
    st.header("Your Upcoming Events")
    upcoming_events = get_user_upcoming_events(user_id)
    if upcoming_events:
        for event in upcoming_events:
            with st.expander(f"{event['title']} - {event['start_time']}"):
                st.write(f"Description: {event['description']}")
                st.write(f"Start: {event['start_time']}")
                st.write(f"End: {event['end_time']}")
                time_until_event = event['start_time'] - datetime.now()
                st.write(f"Time until event: {time_until_event}")
                if st.button(f"View Event {event['id']}", key=f"view_upcoming_{event['id']}"):
                    st.session_state['view_event_id'] = event['id']
                    st.experimental_rerun()
    else:
        st.write("You don't have any upcoming events.")

    # Recommended Events
    st.header("Recommended Events")
    recommended_events = get_recommended_events(user_id)
    if recommended_events:
        for event in recommended_events:
            with st.expander(f"{event['title']} - {event['start_time']}"):
                st.write(f"Description: {event['description']}")
                st.write(f"Start: {event['start_time']}")
                st.write(f"End: {event['end_time']}")
                st.write(f"Price: ${event['price']}")
                if st.button(f"View Event {event['id']}", key=f"view_recommended_{event['id']}"):
                    st.session_state['view_event_id'] = event['id']
                    st.experimental_rerun()
    else:
        st.write("We don't have any recommendations for you at the moment. Try viewing some events!")

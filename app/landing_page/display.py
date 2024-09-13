import streamlit as st
import json
from app.events.event_management import get_event_details, user_has_event_access, get_merchandise_details, add_comment, add_rating
from app.payments.stripe_integration import create_merchandise_checkout_session, create_checkout_session
from app.components.video_player import custom_video_player, get_video_qualities
from app.utils.social_sharing import get_social_share_urls
from app.utils.calendar_integration import create_ical_event, get_google_calendar_url, get_outlook_calendar_url
from app.utils.seo_utils import generate_meta_tags, generate_event_schema, generate_seo_friendly_url
import base64
from app.feedback.feedback_management import create_event_feedback, get_event_feedback, get_average_event_rating
import os

def display_landing_page(event_id):
    user_id = st.session_state.get('user', {}).get('id')
    user_role = st.session_state.get('user', {}).get('role')
    event = get_event_details(event_id, user_id)
    if not event:
        st.error("Event not found")
        return

    # Get the base URL for sharing
    base_url = os.getenv('DOMAIN_NAME', 'mediahost.dodwell.us')

    # Generate SEO-friendly URL
    seo_friendly_url = generate_seo_friendly_url(event['title'])
    event_url = f"https://{base_url}/event/{seo_friendly_url}"

    # Add meta tags
    meta_tags = generate_meta_tags(
        title=event['title'],
        description=event['description'],
        image_url=event.get('image_url'),
        url=event_url
    )
    st.markdown(meta_tags, unsafe_allow_html=True)

    # Add structured data
    event_schema = generate_event_schema(event, f"https://{base_url}")
    st.markdown(event_schema, unsafe_allow_html=True)

    st.title(event['title'])
    st.write(f"Start: {event['start_time']}")
    st.write(f"End: {event['end_time']}")
    st.write(f"Price: ${event['price']}")
    st.write(f"Average Rating: {event['average_rating']:.2f} ({event['total_ratings']} ratings)")

    # Calendar integration
    st.subheader("Add to Calendar")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        ical_data = create_ical_event(event)
        ical_b64 = base64.b64encode(ical_data).decode()
        href = f'data:text/calendar;charset=utf-8;base64,{ical_b64}'
        st.markdown(f'<a href="{href}" download="event.ics">Download iCal</a>', unsafe_allow_html=True)
    
    with col2:
        google_url = get_google_calendar_url(event)
        st.markdown(f'<a href="{google_url}" target="_blank">Add to Google Calendar</a>', unsafe_allow_html=True)
    
    with col3:
        outlook_url = get_outlook_calendar_url(event)
        st.markdown(f'<a href="{outlook_url}" target="_blank">Add to Outlook Calendar</a>', unsafe_allow_html=True)

    # Social sharing
    st.subheader("Share this event")
    share_urls = get_social_share_urls(event_url, event['title'], event['description'])
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"[![Facebook](https://img.icons8.com/color/48/000000/facebook-new.png)]({share_urls['facebook']})")
    with col2:
        st.markdown(f"[![Twitter](https://img.icons8.com/color/48/000000/twitter.png)]({share_urls['twitter']})")
    with col3:
        st.markdown(f"[![LinkedIn](https://img.icons8.com/color/48/000000/linkedin.png)]({share_urls['linkedin']})")

    # Copy link button
    if st.button("Copy event link"):
        st.write(f"Event link: {event_url}")
        st.success("Link copied to clipboard!")

    for block in event['page_blocks']:
        if block['block_type'] == "Header":
            st.header(block['content'])
        elif block['block_type'] == "Text":
            st.write(block['content'])
        elif block['block_type'] == "Image":
            st.image(block['content'])
        elif block['block_type'] == "Video":
            st.video(block['content'])
        elif block['block_type'] == "Button":
            button_data = json.loads(block['content'])
            if st.button(button_data['text']):
                st.markdown(f"[{button_data['text']}]({button_data['url']})")

    if user_role in ['admin', 'content_manager'] or (user_id and user_has_event_access(user_id, event_id)):
        st.subheader("Event Content")
        st.write("You have access to this event. Enjoy the content!")

        st.subheader("Videos")
        for video in event['videos']:
            st.write(f"Title: {video['title']}")
            st.write(f"Description: {video['description']}")
            if video['url']:
                qualities = get_video_qualities(video['url'])
                subtitles = {
                    "en": "path/to/english/subtitles.vtt",
                    "es": "path/to/spanish/subtitles.vtt"
                }
                custom_video_player(video['url'], subtitles=subtitles)
                selected_quality = st.selectbox(f"Select quality for {video['title']}", 
                                                options=[q['label'] for q in qualities],
                                                format_func=lambda x: f"{x}")
                selected_url = next(q['src'] for q in qualities if q['label'] == selected_quality)
                st.write(f"Selected quality: {selected_quality}")
            else:
                st.warning("Video playback is currently unavailable.")

        st.subheader("Merchandise")
        for item in event['merchandise']:
            with st.expander(f"{item['name']} - ${item['price']}"):
                st.write(f"Description: {item['description']}")
                st.write(f"Stock: {item['stock_quantity']}")
                st.image(item['image_url'])
                if st.button(f"Purchase {item['name']}", key=f"purchase_{item['id']}"):
                    if user_id:
                        checkout_session = create_merchandise_checkout_session(item['id'], user_id)
                        if checkout_session:
                            st.write(f"[Proceed to Payment](https://checkout.stripe.com/pay/{checkout_session.id})")
                        else:
                            st.error("Failed to create checkout session.")
                    else:
                        st.warning("Please log in to purchase merchandise.")
        
        # Rating system
        st.subheader("Rate this event")
        user_rating = event.get('user_rating')
        new_rating = st.slider("Your rating", 1, 5, user_rating or 3)
        if st.button("Submit Rating"):
            if add_rating(user_id, event_id, new_rating):
                st.success("Rating submitted successfully!")
                st.rerun()
            else:
                st.error("Failed to submit rating.")

        # Comments section
        st.subheader("Comments")
        for comment in event['comments']:
            st.text(f"{comment['username']} - {comment['created_at']}")
            st.write(comment['content'])
            st.write("---")

        # Add new comment
        new_comment = st.text_area("Add a comment")
        if st.button("Post Comment"):
            if add_comment(user_id, event_id, new_comment):
                st.success("Comment posted successfully!")
                st.rerun()
            else:
                st.error("Failed to post comment.")

        # Display event feedback
        st.subheader("Event Feedback")
        avg_rating = get_average_event_rating(event_id)
        if avg_rating:
            st.write(f"Average Rating: {avg_rating:.2f}")

        feedback_list = get_event_feedback(event_id, limit=5)
        for feedback in feedback_list:
            st.write(f"{feedback['username']} - Rating: {feedback['rating']}")
            st.write(feedback['comment'])
            st.write("---")

        # Feedback form
        st.subheader("Leave Feedback")
        with st.form("event_feedback_form"):
            rating = st.slider("Rating", 1, 5, 3)
            comment = st.text_area("Comment")
            submit_button = st.form_submit_button("Submit Feedback")

        if submit_button:
            if create_event_feedback(user_id, event_id, rating, comment):
                st.success("Feedback submitted successfully!")
                st.rerun()
            else:
                st.error("Failed to submit feedback. Please try again.")

    elif user_id:
        st.warning("You need to purchase this event to access the full content.")
        if st.button("Purchase Event"):
            checkout_session = create_checkout_session(event_id, user_id)
            if checkout_session:
                st.write(f"[Proceed to Payment](https://checkout.stripe.com/pay/{checkout_session.id})")
            else:
                st.error("Failed to create checkout session.")
    else:
        st.warning("Please log in to view or purchase this event.")

    st.subheader("Available Merchandise")
    for item in event['merchandise']:
        st.write(f"Name: {item['name']}")
        st.write(f"Description: {item['description']}")
        st.write(f"Price: ${item['price']}")
        st.image(item['image_url'])
        if st.button(f"Purchase {item['name']} (No event access)", key=f"purchase_no_access_{item['id']}"):
            if user_id:
                checkout_session = create_merchandise_checkout_session(item['id'], user_id)
                if checkout_session:
                    st.write(f"[Proceed to Payment](https://checkout.stripe.com/pay/{checkout_session.id})")
                else:
                    st.error("Failed to create checkout session.")
            else:
                st.warning("Please log in to purchase merchandise.")

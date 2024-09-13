import streamlit as st
from app.feedback.feedback_management import create_platform_feedback, get_platform_feedback, get_average_platform_rating
from app.auth.auth import require_role

@require_role(['admin', 'content_manager', 'viewer'])
def platform_feedback_page():
    st.title("Platform Feedback")

    # Display average platform rating
    avg_rating = get_average_platform_rating()
    if avg_rating:
        st.write(f"Average Platform Rating: {avg_rating:.2f}")

    # Feedback form
    st.subheader("Leave Feedback")
    with st.form("platform_feedback_form"):
        category = st.selectbox("Category", ["User Interface", "Performance", "Features", "Support", "Other"])
        rating = st.slider("Rating", 1, 5, 3)
        comment = st.text_area("Comment")
        submit_button = st.form_submit_button("Submit Feedback")

    if submit_button:
        user_id = st.session_state.get('user', {}).get('id')
        if user_id:
            if create_platform_feedback(user_id, category, rating, comment):
                st.success("Feedback submitted successfully!")
                st.rerun()  # Changed from st.experimental_rerun()
            else:
                st.error("Failed to submit feedback. Please try again.")
        else:
            st.error("You must be logged in to submit feedback.")

    # Display recent feedback
    st.subheader("Recent Feedback")
    feedback_list = get_platform_feedback(limit=5)
    for feedback in feedback_list:
        st.write(f"{feedback['username']} - {feedback['category']} - Rating: {feedback['rating']}")
        st.write(feedback['comment'])
        st.write("---")

if __name__ == "__main__":
    platform_feedback_page()

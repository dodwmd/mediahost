import streamlit as st

def registration_form():
    with st.form("registration_form"):
        username = st.text_input("Username")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        confirm_password = st.text_input("Confirm Password", type="password")
        is_content_provider = st.checkbox("Register as Content Provider")
        submit_button = st.form_submit_button("Register")

    if submit_button:
        if password != confirm_password:
            st.error("Passwords do not match")
            return None
        return {
            "username": username,
            "email": email,
            "password": password,
            "is_content_provider": is_content_provider
        }
    return None

def login_form():
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submit_button = st.form_submit_button("Login")

    if submit_button:
        return {
            "username": username,
            "password": password
        }
    return None

def profile_form(user):
    with st.form("profile_form"):
        email = st.text_input("Email", value=user['email'])
        submit_button = st.form_submit_button("Update Profile")

    if submit_button:
        return {
            "email": email
        }
    return None

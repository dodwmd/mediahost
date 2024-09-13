import streamlit as st

# Define color schemes
light_theme = {
    "primary": "#1E88E5",
    "background": "#FFFFFF",
    "text": "#333333",
    "secondary": "#FFA726",
    "accent": "#4CAF50",
}

dark_theme = {
    "primary": "#90CAF9",
    "background": "#121212",
    "text": "#E0E0E0",
    "secondary": "#FFB74D",
    "accent": "#81C784",
}

def set_theme(is_dark_mode):
    if is_dark_mode:
        theme = dark_theme
    else:
        theme = light_theme

    # Set theme colors
    st.markdown(f"""
    <style>
    :root {{
        --primary-color: {theme["primary"]};
        --background-color: {theme["background"]};
        --text-color: {theme["text"]};
        --secondary-color: {theme["secondary"]};
        --accent-color: {theme["accent"]};
    }}
    body {{
        background-color: var(--background-color);
        color: var(--text-color);
    }}
    .stButton button {{
        background-color: var(--primary-color);
        color: var(--background-color);
    }}
    .stTextInput input, .stTextArea textarea {{
        background-color: var(--background-color);
        color: var(--text-color);
        border-color: var(--primary-color);
    }}
    .stSelectbox select {{
        background-color: var(--background-color);
        color: var(--text-color);
    }}
    .stHeader {{
        color: var(--primary-color);
    }}
    .stSubheader {{
        color: var(--secondary-color);
    }}
    </style>
    """, unsafe_allow_html=True)

def initialize_theme():
    if 'dark_mode' not in st.session_state:
        st.session_state.dark_mode = False

    set_theme(st.session_state.dark_mode)

def toggle_dark_mode():
    st.session_state.dark_mode = not st.session_state.dark_mode
    set_theme(st.session_state.dark_mode)

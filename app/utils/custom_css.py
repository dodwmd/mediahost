def get_custom_css():
    return """
    <style>
    /* General responsive styles */
    .stApp {
        max-width: 100%;
        padding: 1rem;
        box-sizing: border-box;
    }

    /* Responsive text sizes */
    @media (max-width: 768px) {
        h1 {
            font-size: 1.8rem !important;
        }
        h2 {
            font-size: 1.5rem !important;
        }
        p, .stTextInput > div > div > input, .stTextArea > div > div > textarea {
            font-size: 0.9rem !important;
        }
    }

    /* Responsive layout for columns */
    @media (max-width: 768px) {
        .row-widget.stHorizontal {
            flex-direction: column;
        }
        .row-widget.stHorizontal > div {
            width: 100% !important;
            margin-bottom: 1rem;
        }
    }

    /* Responsive buttons */
    .stButton > button {
        width: 100%;
        margin-top: 0.5rem;
    }

    /* Responsive images */
    .stImage > img {
        max-width: 100%;
        height: auto;
    }

    /* Responsive video player */
    .stVideo > video {
        width: 100%;
        height: auto;
    }

    /* Responsive data editor */
    .stDataFrame {
        overflow-x: auto;
    }

    /* Responsive selectbox */
    .stSelectbox > div > div > select {
        max-width: 100%;
    }

    /* Responsive multiselect */
    .stMultiSelect > div > div > div {
        max-width: 100%;
    }

    /* Responsive date input */
    .stDateInput > div > div > input {
        max-width: 100%;
    }

    /* Responsive number input */
    .stNumberInput > div > div > input {
        max-width: 100%;
    }
    </style>
    """

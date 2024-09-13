LANDING_PAGE_TEMPLATES = {
    "basic": [
        {"type": "Header", "content": "Event Title"},
        {"type": "Image", "content": ""},
        {"type": "Text", "content": "Event Description"},
        {"type": "Button", "content": {"text": "Register Now", "url": "#"}},
    ],
    "webinar": [
        {"type": "Header", "content": "Webinar Title"},
        {"type": "Text", "content": "Join us for an exciting webinar!"},
        {"type": "Image", "content": ""},
        {"type": "Text", "content": "Webinar Details"},
        {"type": "Button", "content": {"text": "Register", "url": "#"}},
        {"type": "Text", "content": "Speaker Bio"},
    ],
    "concert": [
        {"type": "Header", "content": "Concert Name"},
        {"type": "Image", "content": ""},
        {"type": "Text", "content": "Get ready for an unforgettable night of music!"},
        {"type": "Text", "content": "Lineup"},
        {"type": "Text", "content": "Venue Information"},
        {"type": "Button", "content": {"text": "Buy Tickets", "url": "#"}},
    ],
}

def get_template(template_name):
    return LANDING_PAGE_TEMPLATES.get(template_name, LANDING_PAGE_TEMPLATES["basic"])

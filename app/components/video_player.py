import streamlit as st
import streamlit.components.v1 as components

def custom_video_player(video_url, poster_url=None, subtitles=None):
    # Load Plyr CSS and JS
    st.markdown(
        """
        <link rel="stylesheet" href="https://cdn.plyr.io/3.6.8/plyr.css" />
        <script src="https://cdn.plyr.io/3.6.8/plyr.polyfilled.js"></script>
        """,
        unsafe_allow_html=True
    )

    # Create a unique ID for the video player
    player_id = f"plyr_player_{hash(video_url)}"

    # Prepare subtitles HTML if provided
    subtitles_html = ""
    if subtitles:
        for lang, url in subtitles.items():
            subtitles_html += f'<track kind="captions" label="{lang}" src="{url}" srclang="{lang}">'

    # HTML for the video player
    video_html = f"""
    <video id="{player_id}" playsinline controls>
        <source src="{video_url}" type="video/mp4" />
        {subtitles_html}
    </video>
    """

    # JavaScript to initialize Plyr with custom options
    js = f"""
    <script>
        document.addEventListener('DOMContentLoaded', function() {{
            const player = new Plyr('#{player_id}', {{
                controls: [
                    'play-large', 'play', 'progress', 'current-time', 'mute', 'volume', 'captions', 'settings', 'pip', 'airplay', 'fullscreen'
                ],
                settings: ['captions', 'quality', 'speed'],
                speed: {{ selected: 1, options: [0.5, 0.75, 1, 1.25, 1.5, 2] }},
                quality: {{ default: 576, options: [4320, 2880, 2160, 1440, 1080, 720, 576, 480, 360, 240] }}
            }});
        }});
    </script>
    """

    # Combine HTML and JavaScript
    full_html = f"{video_html}{js}"

    # Use Streamlit's components.html to render the custom player
    components.html(full_html, height=400)

def get_video_qualities(video_url):
    # This is a placeholder function. In a real-world scenario, you would
    # implement logic to determine available video qualities.
    # For now, we'll return some dummy qualities.
    return [
        {"label": "4K", "src": f"{video_url}?quality=4k"},
        {"label": "1080p", "src": f"{video_url}?quality=1080p"},
        {"label": "720p", "src": f"{video_url}?quality=720p"},
        {"label": "480p", "src": f"{video_url}?quality=480p"},
    ]

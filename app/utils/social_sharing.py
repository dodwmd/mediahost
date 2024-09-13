import urllib.parse

def get_social_share_urls(event_url, title, description):
    encoded_url = urllib.parse.quote(event_url)
    encoded_title = urllib.parse.quote(title)
    encoded_description = urllib.parse.quote(description)

    facebook_url = f"https://www.facebook.com/sharer/sharer.php?u={encoded_url}"
    twitter_url = f"https://twitter.com/intent/tweet?url={encoded_url}&text={encoded_title}"
    linkedin_url = f"https://www.linkedin.com/shareArticle?mini=true&url={encoded_url}&title={encoded_title}&summary={encoded_description}"

    return {
        "facebook": facebook_url,
        "twitter": twitter_url,
        "linkedin": linkedin_url
    }

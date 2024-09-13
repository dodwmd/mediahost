import json
from urllib.parse import quote

def generate_meta_tags(title, description, image_url=None, url=None):
    meta_tags = f"""
    <title>{title}</title>
    <meta name="description" content="{description}">
    <meta property="og:title" content="{title}">
    <meta property="og:description" content="{description}">
    <meta property="og:type" content="website">
    """
    if url:
        meta_tags += f'<meta property="og:url" content="{url}">\n'
    if image_url:
        meta_tags += f'<meta property="og:image" content="{image_url}">\n'
    return meta_tags

def generate_event_schema(event, base_url):
    schema = {
        "@context": "https://schema.org",
        "@type": "Event",
        "name": event['title'],
        "description": event['description'],
        "startDate": event['start_time'].isoformat(),
        "endDate": event['end_time'].isoformat(),
        "location": {
            "@type": "VirtualLocation",
            "url": f"{base_url}/event/{generate_seo_friendly_url(event['title'])}"
        },
        "organizer": {
            "@type": "Organization",
            "name": event.get('content_provider_name', 'Event Organizer')
        },
        "offers": {
            "@type": "Offer",
            "price": str(event['price']),
            "priceCurrency": "USD",
            "availability": "https://schema.org/InStock",
            "url": f"{base_url}/event/{generate_seo_friendly_url(event['title'])}"
        }
    }
    return f'<script type="application/ld+json">{json.dumps(schema)}</script>'

def generate_seo_friendly_url(title):
    return quote(title.lower().replace(" ", "-"))

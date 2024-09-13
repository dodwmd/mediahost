from app.database.db import execute_query
from app.utils.seo_utils import generate_seo_friendly_url
import xml.etree.ElementTree as ET
from datetime import datetime
import os

def generate_sitemap():
    domain = os.getenv('DOMAIN_NAME', 'mediahost.dodwell.us')
    root = ET.Element("urlset")
    root.set("xmlns", "http://www.sitemaps.org/schemas/sitemap/0.9")

    # Add static pages
    static_pages = ["/", "/events", "/faq", "/blog"]
    for page in static_pages:
        url = ET.SubElement(root, "url")
        loc = ET.SubElement(url, "loc")
        loc.text = f"https://{domain}{page}"
        lastmod = ET.SubElement(url, "lastmod")
        lastmod.text = datetime.now().strftime("%Y-%m-%d")

    # Add event pages
    events = execute_query("SELECT id, title, updated_at FROM events WHERE is_published = TRUE")
    for event in events:
        url = ET.SubElement(root, "url")
        loc = ET.SubElement(url, "loc")
        seo_friendly_url = generate_seo_friendly_url(event['title'])
        loc.text = f"https://{domain}/event/{seo_friendly_url}"
        lastmod = ET.SubElement(url, "lastmod")
        lastmod.text = event['updated_at'].strftime("%Y-%m-%d")

    # Add blog post pages
    blog_posts = execute_query("SELECT id, title, updated_at FROM blog_posts WHERE is_published = TRUE")
    for post in blog_posts:
        url = ET.SubElement(root, "url")
        loc = ET.SubElement(url, "loc")
        seo_friendly_url = generate_seo_friendly_url(post['title'])
        loc.text = f"https://{domain}/blog/{seo_friendly_url}"
        lastmod = ET.SubElement(url, "lastmod")
        lastmod.text = post['updated_at'].strftime("%Y-%m-%d")

    return ET.tostring(root, encoding="unicode")

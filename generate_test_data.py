import os
import random
from datetime import datetime, timedelta
import requests
from faker import Faker
from app.database.db import execute_query
from app.storage.minio_client import upload_file
from dotenv import load_dotenv
import bcrypt
import json
from app.feedback.feedback_management import create_event_feedback, create_platform_feedback

load_dotenv()

fake = Faker()

# Configuration
NUM_USERS = 10
NUM_CONTENT_PROVIDERS = 3
NUM_EVENTS_PER_PROVIDER = 2
NUM_VIDEOS_PER_EVENT = 2
NUM_MERCHANDISE_PER_EVENT = 2

# Sample video and image URLs
SAMPLE_VIDEOS = [
    "https://sample-videos.com/video123/mp4/720/big_buck_bunny_720p_1mb.mp4",
    "https://sample-videos.com/video123/mp4/720/big_buck_bunny_720p_2mb.mp4",
    "https://sample-videos.com/video123/mp4/720/big_buck_bunny_720p_5mb.mp4",
]

SAMPLE_IMAGES = [
    "https://picsum.photos/200/300",
    "https://picsum.photos/300/200",
    "https://picsum.photos/250/250",
]

def create_tables():
    sql_dir = os.path.join('config', 'sql')
    for sql_file in sorted(os.listdir(sql_dir)):
        if sql_file.endswith('.sql'):
            with open(os.path.join(sql_dir, sql_file), 'r') as f:
                sql_script = f.read()
                print(f"Executing SQL from {sql_file}:")
                print(sql_script)
                try:
                    execute_query(sql_script)
                    print(f"Successfully executed {sql_file}")
                except Exception as e:
                    print(f"Error executing {sql_file}: {str(e)}")

def create_users():
    users = []
    roles = {'admin': 1, 'content_manager': 2, 'viewer': 3}
    for i in range(NUM_USERS):
        username = fake.user_name()
        email = fake.email()
        password = fake.password()
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        if i == 0:
            role_id = roles['admin']
        elif i < NUM_CONTENT_PROVIDERS:
            role_id = roles['content_manager']
        else:
            role_id = roles['viewer']

        query = """
        INSERT INTO users (username, email, password_hash, role_id, is_content_provider)
        VALUES (%s, %s, %s, %s, %s)
        """
        params = (username, email, hashed_password, role_id, role_id == roles['content_manager'])
        user_id = execute_query(query, params)
        users.append((user_id, role_id))
    return users

def create_sample_categories():
    categories = [
        "Music", "Technology", "Business", "Sports", "Arts",
        "Food & Drink", "Health & Wellness", "Education", "Entertainment", "Networking"
    ]
    for category in categories:
        query = "INSERT INTO categories (name) VALUES (%s) ON DUPLICATE KEY UPDATE name = VALUES(name)"
        execute_query(query, (category,))

def create_sample_tags():
    sample_tags = [
        "Virtual", "In-Person", "Webinar", "Conference", "Workshop",
        "Networking", "Tech", "Business", "Creative", "Health",
        "Education", "Entertainment", "Charity", "Sports", "Music"
    ]
    for tag in sample_tags:
        query = "INSERT INTO tags (name) VALUES (%s) ON DUPLICATE KEY UPDATE name = VALUES(name)"
        execute_query(query, (tag,))

def create_events(content_providers):
    events = []
    categories = execute_query("SELECT id FROM categories")
    tags = execute_query("SELECT id FROM tags")
    for user_id, _ in content_providers:
        for _ in range(NUM_EVENTS_PER_PROVIDER):
            title = fake.sentence(nb_words=4)
            description = fake.paragraph()
            start_time = fake.future_datetime(end_date="+180d")
            duration = timedelta(hours=random.randint(1, 8))
            end_time = start_time + duration
            price = round(random.uniform(0, 500), 2)
            is_published = random.choice([True, True, True, False])

            query = """
            INSERT INTO events (content_provider_id, title, description, start_time, end_time, price, is_published)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            params = (user_id, title, description, start_time, end_time, price, is_published)
            event_id = execute_query(query, params)
            
            if event_id:
                events.append(event_id)
                
                # Assign random categories to the event
                num_categories = random.randint(1, 5)
                event_categories = random.sample(categories, num_categories)
                for category in event_categories:
                    query = "INSERT INTO event_categories (event_id, category_id) VALUES (%s, %s)"
                    execute_query(query, (event_id, category['id']))
                
                # Assign random tags to the event
                num_tags = random.randint(1, 5)
                event_tags = random.sample(tags, num_tags)
                for tag in event_tags:
                    query = "INSERT INTO event_tags (event_id, tag_id) VALUES (%s, %s)"
                    execute_query(query, (event_id, tag['id']))
    
    return events

def download_and_upload_file(url, bucket_name):
    response = requests.get(url)
    if response.status_code == 200:
        file_name = os.path.basename(url)
        file_data = response.content
        file_path = upload_file(file_data, file_name, bucket_name)
        return file_path
    return None

def create_videos(events):
    for event_id in events:
        for _ in range(NUM_VIDEOS_PER_EVENT):
            title = fake.sentence()
            description = fake.paragraph()
            duration = random.randint(60, 3600)
            video_url = random.choice(SAMPLE_VIDEOS)
            file_path = download_and_upload_file(video_url, "videos")

            if file_path:
                # Sample video qualities
                qualities = [
                    {"label": "4K", "src": f"{file_path}?quality=4k"},
                    {"label": "1080p", "src": f"{file_path}?quality=1080p"},
                    {"label": "720p", "src": f"{file_path}?quality=720p"},
                    {"label": "480p", "src": f"{file_path}?quality=480p"},
                ]

                # Sample subtitles
                subtitles = {
                    "en": f"{file_path}_en.vtt",
                    "es": f"{file_path}_es.vtt",
                }

                query = """
                INSERT INTO videos (event_id, title, description, file_path, duration, qualities, subtitles)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """
                params = (event_id, title, description, file_path, duration, json.dumps(qualities), json.dumps(subtitles))
                execute_query(query, params)

def create_merchandise(events):
    for event_id in events:
        for _ in range(NUM_MERCHANDISE_PER_EVENT):
            name = fake.word()  # Use word() instead of product_name()
            description = fake.paragraph()
            price = round(random.uniform(5, 50), 2)
            stock_quantity = random.randint(10, 100)
            image_url = random.choice(SAMPLE_IMAGES)
            image_path = download_and_upload_file(image_url, "merchandise")

            if image_path:
                query = """
                INSERT INTO merchandise (event_id, name, description, price, stock_quantity, image_path)
                VALUES (%s, %s, %s, %s, %s, %s)
                """
                params = (event_id, name, description, price, stock_quantity, image_path)
                execute_query(query, params)

def create_page_blocks(events):
    for event_id in events:
        blocks = [
            ("Header", fake.catch_phrase(), {"font": "Arial", "font_size": 36, "color": "#000000"}),
            ("Text", fake.paragraph(), {"font": "Helvetica", "font_size": 16, "color": "#333333", "alignment": "left"}),
            ("Image", random.choice(SAMPLE_IMAGES), {"width": 80, "alignment": "center"}),
            ("Text", fake.paragraph(), {"font": "Helvetica", "font_size": 16, "color": "#333333", "alignment": "left"}),
            ("Button", json.dumps({"text": "Buy Now", "url": f"/event/{event_id}"}), {"background_color": "#4CAF50", "text_color": "#FFFFFF", "border_radius": 4})
        ]
        for index, (block_type, content, styles) in enumerate(blocks):
            query = """
            INSERT INTO page_blocks (event_id, block_type, content, order_index, styles)
            VALUES (%s, %s, %s, %s, %s)
            """
            params = (event_id, block_type, content, index, json.dumps(styles))
            execute_query(query, params)

def create_sample_comments_and_ratings(events, users):
    for event_id in events:
        for _ in range(random.randint(0, 5)):  # 0 to 5 comments per event
            user_id = random.choice(users)[0]
            content = fake.paragraph()
            query = """
            INSERT INTO comments (user_id, event_id, content)
            VALUES (%s, %s, %s)
            """
            execute_query(query, (user_id, event_id, content))
        
        for _ in range(random.randint(0, 10)):  # 0 to 10 ratings per event
            user_id = random.choice(users)[0]
            rating = random.randint(1, 5)
            query = """
            INSERT INTO ratings (user_id, event_id, rating)
            VALUES (%s, %s, %s)
            ON DUPLICATE KEY UPDATE rating = VALUES(rating)
            """
            execute_query(query, (user_id, event_id, rating))
        
        # Update average rating and total ratings for the event
        query = """
        UPDATE events e
        SET average_rating = (SELECT AVG(rating) FROM ratings WHERE event_id = e.id),
            total_ratings = (SELECT COUNT(*) FROM ratings WHERE event_id = e.id)
        WHERE e.id = %s
        """
        execute_query(query, (event_id,))

def generate_sample_analytics_data(events, users):
    for event in events:
        # Generate sample views
        for _ in range(random.randint(50, 200)):
            user_id = random.choice(users)[0]
            timestamp = fake.date_time_between(start_date='-30d', end_date='now')
            query = """
            INSERT INTO event_views (event_id, user_id, timestamp)
            VALUES (%s, %s, %s)
            """
            execute_query(query, (event, user_id, timestamp))

def create_notification(user_id, message, notification_type, related_id=None):
    query = """
    INSERT INTO notifications (user_id, message, notification_type, related_id, created_at, is_read)
    VALUES (%s, %s, %s, %s, %s, %s)
    """
    params = (user_id, message, notification_type, related_id, datetime.now(), False)
    return execute_query(query, params)

def create_sample_notifications(users, events):
    for user in users:
        user_id = user[0]
        for _ in range(random.randint(1, 5)):
            event = random.choice(events)
            message = f"New event '{fake.catch_phrase()}' has been added!"
            create_notification(user_id, message, 'new_event', event)

def create_blog_post(author_id, title, content, is_published=False):
    query = """
    INSERT INTO blog_posts (author_id, title, content, is_published, created_at, updated_at)
    VALUES (%s, %s, %s, %s, %s, %s)
    """
    params = (author_id, title, content, is_published, datetime.now(), datetime.now())
    return execute_query(query, params)

def create_sample_blog_posts(users):
    content_providers = [user for user in users if user[1] in [1, 2]]  # Admin and content manager roles
    for _ in range(10):  # Create 10 sample blog posts
        author = random.choice(content_providers)
        title = fake.sentence()
        content = "\n\n".join(fake.paragraphs(nb=3))
        is_published = random.choice([True, False])
        create_blog_post(author[0], title, content, is_published)

def create_sample_feedback(users, events):
    for _ in range(20):  # Create 20 sample event feedbacks
        user = random.choice(users)
        event = random.choice(events)
        rating = random.randint(1, 5)
        comment = fake.paragraph()
        create_event_feedback(user[0], event, rating, comment)

    categories = ["User Interface", "Performance", "Features", "Support", "Other"]
    for _ in range(10):  # Create 10 sample platform feedbacks
        user = random.choice(users)
        category = random.choice(categories)
        rating = random.randint(1, 5)
        comment = fake.paragraph()
        create_platform_feedback(user[0], category, rating, comment)

def main():
    print("Creating tables...")
    create_tables()

    print("Creating sample categories...")
    create_sample_categories()

    print("Creating sample tags...")
    create_sample_tags()

    print("Generating test data...")
    users = create_users()
    content_providers = [user for user in users if user[1] in [1, 2]]  # Admin and content manager roles
    events = create_events(content_providers)
    create_videos(events)
    create_merchandise(events)
    create_page_blocks(events)
    create_sample_comments_and_ratings(events, users)
    generate_sample_analytics_data(events, users)
    create_sample_notifications(users, events)
    create_sample_blog_posts(users)
    create_sample_feedback(users, events)
    print("Test data generation complete!")

if __name__ == "__main__":
    main()

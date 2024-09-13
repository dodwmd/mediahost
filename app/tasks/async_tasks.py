import asyncio
from app.messaging.nats_client import nats_client
import json

async def process_video(msg):
    data = json.loads(msg.data.decode())
    video_id = data['video_id']
    file_path = data['file_path']
    event_id = data['event_id']
    
    print(f"Processing video {video_id} for event {event_id}")
    # Add your video processing logic here
    # For example, you could generate thumbnails, transcode the video, etc.
    
    # After processing, you could update the video status in the database
    # and publish a message to notify that processing is complete

async def send_email_notification(msg):
    data = json.loads(msg.data.decode())
    event_id = data['event_id']
    event_title = data['event_title']
    video_title = data['video_title']
    
    print(f"Sending email notification for new video '{video_title}' in event '{event_title}'")
    # Add your email sending logic here

async def update_analytics(msg):
    data = json.loads(msg.data.decode())
    event_id = data['event_id']
    action = data['action']
    is_published = data['is_published']
    
    print(f"Updating analytics for event {event_id}: action={action}, is_published={is_published}")
    # Add your analytics update logic here

async def start_workers():
    await nats_client.subscribe("video.processing", process_video)
    await nats_client.subscribe("email.notification", send_email_notification)
    await nats_client.subscribe("analytics.event_update", update_analytics)

# Start the workers
asyncio.run(start_workers())

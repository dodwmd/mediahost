import asyncio
import nats
from nats.errors import ConnectionClosedError, TimeoutError, NoServersError
import os
from dotenv import load_dotenv

load_dotenv()

class NatsClient:
    def __init__(self):
        self.nc = None
        self.js = None

    async def connect(self):
        try:
            self.nc = await nats.connect(os.getenv('NATS_URL'))
            self.js = self.nc.jetstream()
            print("Connected to NATS")
        except Exception as e:
            print(f"Error connecting to NATS: {e}")

    async def publish(self, subject, message):
        try:
            await self.js.publish(subject, message.encode())
            print(f"Published message to {subject}")
        except Exception as e:
            print(f"Error publishing message: {e}")

    async def subscribe(self, subject, callback):
        try:
            await self.js.subscribe(subject, cb=callback)
            print(f"Subscribed to {subject}")
        except Exception as e:
            print(f"Error subscribing to {subject}: {e}")

    async def close(self):
        if self.nc:
            await self.nc.close()
            print("Closed NATS connection")

nats_client = NatsClient()

async def initialize_nats():
    await nats_client.connect()

# Helper function to publish messages
def publish_message(subject, message):
    asyncio.run(nats_client.publish(subject, message))

# Example callback function for processing messages
async def process_message(msg):
    subject = msg.subject
    data = msg.data.decode()
    print(f"Received a message on '{subject}': {data}")
    # Add your message processing logic here

# Initialize NATS connection
asyncio.run(initialize_nats())

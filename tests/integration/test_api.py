import unittest
from app.api.swagger_docs import app

class TestAPI(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_get_events(self):
        response = self.client.get('/events/')
        self.assertEqual(response.status_code, 200)

    def test_create_event(self):
        event_data = {
            "title": "Test Event",
            "description": "Test Description",
            "start_time": "2023-01-01T12:00:00",
            "end_time": "2023-01-01T14:00:00",
            "price": 10.0,
            "is_published": True
        }
        response = self.client.post('/events/', json=event_data)
        self.assertEqual(response.status_code, 201)

    def test_get_users(self):
        response = self.client.get('/users/')
        self.assertEqual(response.status_code, 200)

    def test_get_videos(self):
        response = self.client.get('/videos/')
        self.assertEqual(response.status_code, 200)

if __name__ == '__main__':
    unittest.main()

import unittest
from app.database.db import execute_query
from app.auth.auth import register_user, login_user

class TestDatabase(unittest.TestCase):
    def setUp(self):
        # Set up test database or use a separate test database
        pass

    def tearDown(self):
        # Clean up test data
        execute_query("DELETE FROM users WHERE username LIKE 'test%'")

    def test_user_registration_and_login(self):
        # Test user registration
        username = "testuser"
        email = "testuser@example.com"
        password = "testpassword"
        result = register_user(username, email, password)
        self.assertTrue(result)

        # Test user login
        login_result = login_user(username, password)
        self.assertIsNotNone(login_result)
        self.assertEqual(login_result['user']['username'], username)

    def test_event_creation_and_retrieval(self):
        # First, create a test user
        user_id = register_user("testeventuser", "testeventuser@example.com", "testpassword")

        # Create a test event
        from app.events.event_management import create_event, get_events_by_provider
        event_result = create_event(user_id, "Test Event", "Test Description", "2023-01-01 12:00:00", "2023-01-01 14:00:00", 10.0, [], [])
        self.assertTrue(event_result)

        # Retrieve events for the user
        events = get_events_by_provider(user_id)
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0]['title'], "Test Event")

if __name__ == '__main__':
    unittest.main()

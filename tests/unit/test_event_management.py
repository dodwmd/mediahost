import unittest
from unittest.mock import patch
from app.events.event_management import create_event, get_events_by_provider, update_event, delete_event

class TestEventManagement(unittest.TestCase):
    @patch('app.events.event_management.execute_query')
    def test_create_event(self, mock_execute_query):
        mock_execute_query.return_value = 1
        result = create_event(1, "Test Event", "Description", "2023-01-01 12:00:00", "2023-01-01 14:00:00", 10.0, [1], [1])
        self.assertTrue(result)

    @patch('app.events.event_management.execute_query')
    def test_get_events_by_provider(self, mock_execute_query):
        mock_execute_query.return_value = [
            {"id": 1, "title": "Event 1"},
            {"id": 2, "title": "Event 2"}
        ]
        events = get_events_by_provider(1)
        self.assertEqual(len(events), 2)
        self.assertEqual(events[0]["title"], "Event 1")

    @patch('app.events.event_management.execute_query')
    def test_update_event(self, mock_execute_query):
        mock_execute_query.return_value = True
        result = update_event(1, "Updated Event", "New Description", "2023-01-01 12:00:00", "2023-01-01 14:00:00", 15.0, True, [1], [1])
        self.assertTrue(result)

    @patch('app.events.event_management.execute_query')
    def test_delete_event(self, mock_execute_query):
        mock_execute_query.return_value = True
        result = delete_event(1)
        self.assertTrue(result)

if __name__ == '__main__':
    unittest.main()

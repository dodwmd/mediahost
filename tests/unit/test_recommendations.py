import unittest
from unittest.mock import patch
from app.recommendations.recommendation_engine import get_recommended_events

class TestRecommendations(unittest.TestCase):
    @patch('app.recommendations.recommendation_engine.execute_query')
    def test_get_recommended_events(self, mock_execute_query):
        mock_execute_query.side_effect = [
            [{"id": 1, "title": "Event 1"}],  # viewed events
            [{"id": 1, "name": "Category 1"}],  # categories
            [{"id": 1, "title": "Recommended Event 1"}],  # recommended events
            [{"id": 2, "title": "Popular Event 1"}]  # popular events
        ]
        
        recommendations = get_recommended_events(1)
        self.assertEqual(len(recommendations), 2)
        self.assertEqual(recommendations[0]["title"], "Recommended Event 1")
        self.assertEqual(recommendations[1]["title"], "Popular Event 1")

if __name__ == '__main__':
    unittest.main()

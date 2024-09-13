import unittest
from unittest.mock import patch
from app.auth.auth import hash_password, verify_password, create_access_token, get_user_role

class TestAuth(unittest.TestCase):
    def test_hash_password(self):
        password = "testpassword"
        hashed = hash_password(password)
        self.assertNotEqual(password, hashed)
        self.assertTrue(verify_password(password, hashed))

    def test_verify_password(self):
        password = "testpassword"
        hashed = hash_password(password)
        self.assertTrue(verify_password(password, hashed))
        self.assertFalse(verify_password("wrongpassword", hashed))

    @patch('app.auth.auth.jwt.encode')
    def test_create_access_token(self, mock_encode):
        mock_encode.return_value = "mocked_token"
        token = create_access_token({"sub": "testuser"})
        self.assertEqual(token, "mocked_token")

    @patch('app.auth.auth.execute_query')
    def test_get_user_role(self, mock_execute_query):
        mock_execute_query.return_value = [{"name": "admin"}]
        role = get_user_role(1)
        self.assertEqual(role, "admin")

        mock_execute_query.return_value = []
        role = get_user_role(2)
        self.assertIsNone(role)

if __name__ == '__main__':
    unittest.main()

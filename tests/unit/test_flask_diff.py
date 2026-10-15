import base64
import os
import tempfile
import unittest

from help_window.flask_server_files.flask_app import create_app
from help_window.help_app import HeadlessHelpApp


class TestFlaskDiff(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.content_dir = os.path.join(self.temp_dir.name, "help_content")
        os.makedirs(self.content_dir)

        # Mock HelpApp
        self.app_instance = HeadlessHelpApp(content_dir=self.content_dir)

        # Create Flask app
        self.flask_app = create_app(self.app_instance)
        self.flask_app.config['TESTING'] = True
        self.client = self.flask_app.test_client()

        # Auth header (matching help_server_settings in untracked_config)
        self.auth_headers = {
            'Authorization': 'Basic ' + base64.b64encode(b"admin:password123").decode('ascii')
        }

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_get_file_diff_non_text(self):
        """Verify that non-text files return diff: null."""
        response = self.client.get('/api/versions/file_diff?path=image.png&old_hash=h1&new_hash=h2',
                                   headers=self.auth_headers)
        self.assertEqual(response.status_code, 200)
        data = response.json
        self.assertIsNone(data['diff'])

    def test_get_file_diff_json(self):
        """Verify that JSON files return a text diff (even if empty if hashes don't exist)."""
        response = self.client.get('/api/versions/file_diff?path=article.json&old_hash=h1&new_hash=h2',
                                   headers=self.auth_headers)
        self.assertEqual(response.status_code, 200)
        data = response.json
        self.assertIsInstance(data['diff'], str)

    def test_get_file_diff_txt(self):
        """Verify that text files return a text diff."""
        response = self.client.get('/api/versions/file_diff?path=notes.txt&old_hash=h1&new_hash=h2',
                                   headers=self.auth_headers)
        self.assertEqual(response.status_code, 200)
        data = response.json
        self.assertIsInstance(data['diff'], str)

    def test_get_file_diff_unauthorized(self):
        """Verify that unauthorized requests are rejected."""
        response = self.client.get('/api/versions/file_diff?path=article.json&old_hash=h1&new_hash=h2')
        self.assertEqual(response.status_code, 401)


if __name__ == "__main__":
    unittest.main()

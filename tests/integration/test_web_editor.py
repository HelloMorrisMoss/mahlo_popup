import json
import os
import threading
import time
import unittest

import requests

from help_window.help_app import HelpApp
from untracked_config.configuration_data import help_api_port


class TestWebEditor(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # We need a HelpApp instance to start the Flask server
        # but we don't want to actually start the Tkinter mainloop
        cls.app = HelpApp(enable_editor=True)
        cls.flask_thread = threading.Thread(
            target=cls.app.after,
            args=(0, lambda: None)  # Dummy call to keep it alive? No, we need start_flask_server
        )
        # Actually, let's just start the flask server directly
        from help_window.flask_server_files.flask_app import start_flask_server
        cls.server_thread = threading.Thread(
            target=start_flask_server,
            args=(cls.app,),
            daemon=True
        )
        cls.server_thread.start()
        time.sleep(2)  # Wait for server to start

    def test_get_articles(self):
        response = requests.get(f"http://localhost:{help_api_port}/api/articles")
        self.assertEqual(response.status_code, 200)
        articles = response.json()
        self.assertIsInstance(articles, list)

    def test_create_and_load_article(self):
        # Create
        title = "Test Web Article"
        response = requests.post(f"http://localhost:{help_api_port}/api/create_article",
                                 json={"title": title})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        file_path = data['file_path']
        self.assertTrue(os.path.exists(file_path))

        # Load
        response = requests.get(f"http://localhost:{help_api_port}/api/article?path={file_path}")
        self.assertEqual(response.status_code, 200)
        content = response.json()
        self.assertEqual(content[0]['type'], 'title')
        self.assertEqual(content[0]['content'], title)

        # Cleanup
        os.remove(file_path)

    def test_save_article(self):
        # Create temp file
        temp_path = os.path.join(self.app.content_manager.content_dir, "temp_save_test.json")
        initial_content = [{"type": "title", "content": "Temp"}]
        with open(temp_path, 'w', encoding='utf-8') as f:
            json.dump(initial_content, f)

        new_content = [{"type": "title", "content": "Updated"}, {"type": "paragraph", "content": "New content"}]
        response = requests.post(f"http://localhost:{help_api_port}/api/article",
                                 json={"path": temp_path, "content": new_content})
        self.assertEqual(response.status_code, 200)

        # Verify
        with open(temp_path, 'r', encoding='utf-8') as f:
            saved_content = json.load(f)
        self.assertEqual(saved_content, new_content)

        # Cleanup
        os.remove(temp_path)


if __name__ == "__main__":
    unittest.main()

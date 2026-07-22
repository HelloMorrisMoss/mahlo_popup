import json
import os
import shutil
import tkinter as tk
import unittest
from unittest.mock import MagicMock, patch

from help_window.editor.editor_manager import EditorManager


class TestEditorManager(unittest.TestCase):
    def setUp(self):
        self.root = tk.Tk()
        self.test_dir = os.path.join(os.getcwd(), "test_help_content")
        os.makedirs(self.test_dir, exist_ok=True)

        self.cm = MagicMock()
        self.cm.content_dir = self.test_dir

        self.em = EditorManager(self.root, self.cm)

    def tearDown(self):
        self.root.destroy()
        shutil.rmtree(self.test_dir)

    @patch('tkinter.simpledialog.askstring')
    def test_new_article_uses_title_block(self, mock_askstring):
        """Verify that New Article creates a JSON with a title block."""
        mock_askstring.return_value = "new_test_article"

        # We need to mock _refresh_tree because it interacts with the UI
        self.em._refresh_tree = MagicMock()
        # We also mock _open_editor to avoid launching the ArticleEditor window
        self.em._open_editor = MagicMock()

        self.em._new_article()

        file_path = os.path.join(self.test_dir, "new_test_article.json")
        self.assertTrue(os.path.exists(file_path))

        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        self.assertEqual(data[0]["type"], "title")
        self.assertEqual(data[0]["content"], "new_test_article")


if __name__ == "__main__":
    unittest.main()

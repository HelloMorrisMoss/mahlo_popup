import tkinter as tk
import unittest
from tkinter import ttk
from unittest.mock import MagicMock, patch

from help_window.help_frame import HelpFrame


class TestHelpFrameRefresh(unittest.TestCase):
    def setUp(self):
        self.root = tk.Tk()
        self.content_manager = MagicMock()
        # Mock articles
        self.article1 = {"title": "Article 1", "file_path": "art1.json"}
        self.article2 = {"title": "Article 2", "file_path": "art2.json"}
        self.content_manager.scan_content.return_value = [self.article1, self.article2]
        self.content_manager.articles = [self.article1, self.article2]
        self.content_manager.content_dir = "mock_dir"

        # Patch NavFrame and ArticleViewer to avoid TK errors and complex init
        with patch('help_window.help_frame.NavFrame') as mock_nav, \
                patch('help_window.help_frame.ArticleViewer') as mock_viewer:
            # Make the mocks behave like widgets enough for PanedWindow
            nav_frame = ttk.Frame(self.root)
            nav_frame.populate = MagicMock()
            nav_frame.select_article = MagicMock()
            mock_nav.return_value = nav_frame

            viewer = ttk.Frame(self.root)
            viewer.load_article = MagicMock()
            mock_viewer.return_value = viewer

            self.frame = HelpFrame(self.root, self.content_manager)

    def tearDown(self):
        self.root.destroy()

    def test_refresh_list_reloads_current_article(self):
        """Verify that refresh_list reloads the active article if it still exists."""
        # Set current article
        self.frame.current_article = self.article1

        # Mock what happens when we select an article
        self.frame._on_article_selected = MagicMock()

        # Trigger refresh
        self.frame.refresh_list()

        # Verify scan_content was called
        self.content_manager.scan_content.assert_called()

        # Verify the current article was re-selected and re-loaded
        self.frame.nav_frame.select_article.assert_called_with("art1.json")
        self.frame._on_article_selected.assert_called_with(self.article1)

    def test_refresh_list_handles_removed_article(self):
        """Verify that refresh_list doesn't crash if current article is gone."""
        self.frame.current_article = {"title": "Gone", "file_path": "gone.json"}
        self.frame._on_article_selected = MagicMock()

        # Trigger refresh with new list not containing 'gone.json'
        self.content_manager.scan_content.return_value = [self.article1, self.article2]
        self.frame.refresh_list()

        # Should NOT call select_article for the gone one
        self.frame._on_article_selected.assert_not_called()


if __name__ == '__main__':
    unittest.main()

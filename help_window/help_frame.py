from tkinter import ttk
from typing import Dict

from help_window.article_viewer import ArticleViewer
from help_window.content_manager import ContentManager
from help_window.nav_frame import NavFrame


class HelpFrame(ttk.Frame):
    """
    Main container for the Help Window UI.
    Contains NavFrame and ArticleViewer in a side-by-side layout.
    """

    def __init__(self, parent, content_manager: ContentManager, **kwargs):
        super().__init__(parent, **kwargs)
        self.content_manager = content_manager

        # Use PanedWindow for resizable side-by-side layout
        self.paned = ttk.PanedWindow(self, orient="horizontal")
        self.paned.pack(fill="both", expand=True)

        # Left side: Navigation
        self.nav_frame = NavFrame(self.paned, on_select=self._on_article_selected)
        self.paned.add(self.nav_frame, weight=1)

        # Right side: Content
        self.viewer = ArticleViewer(self.paned, on_link_click=self._on_link_clicked)
        self.paned.add(self.viewer, weight=4)

        # Load initial content
        self.refresh_list()
        self._load_default_article()

    def refresh_list(self):
        """Refreshes the article list from the content manager."""
        articles = self.content_manager.scan_content()
        self.nav_frame.populate(articles)

    def _on_article_selected(self, article_meta: Dict):
        """Callback when an article is selected in the NavFrame."""
        file_path = article_meta.get("file_path")
        title = article_meta.get("title", "Untitled")
        content = self.content_manager.load_article_content(file_path)
        self.viewer.load_article(title, content)

    def _on_link_clicked(self, target_path: str):
        """Callback for inter-article links."""
        # Target path could be relative to content dir or absolute
        # For now, let's try to find it in the scanned articles
        found = False
        target_abs = os.path.abspath(target_path)

        for article in self.content_manager.articles:
            if os.path.abspath(article["file_path"]) == target_abs:
                self.nav_frame.select_article(article["file_path"])
                self._on_article_selected(article)
                found = True
                break

        if not found:
            # Maybe it's relative to content_dir
            target_rel = os.path.join(self.content_manager.content_dir, target_path)
            target_rel_abs = os.path.abspath(target_rel)
            for article in self.content_manager.articles:
                if os.path.abspath(article["file_path"]) == target_rel_abs:
                    self.nav_frame.select_article(article["file_path"])
                    self._on_article_selected(article)
                    found = True
                    break

    def _load_default_article(self):
        """Loads the 'help for help' article or the first one in the list."""
        if not self.content_manager.articles:
            return

        # Look for 'help_for_help.json'
        default_article = None
        for article in self.content_manager.articles:
            if "help_for_help.json" in article["file_path"]:
                default_article = article
                break

        if not default_article:
            default_article = self.content_manager.articles[0]

        self.nav_frame.select_article(default_article["file_path"])
        self._on_article_selected(default_article)

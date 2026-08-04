import os
import tkinter as tk
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

    def __init__(self, parent, content_manager: ContentManager, enable_editor: bool = False, server_url: str = None,
                 **kwargs):
        super().__init__(parent, **kwargs)
        self.content_manager = content_manager
        self.parent = parent  # Usually the HelpApp (tk.Tk)
        self.enable_editor = enable_editor
        self.server_url = server_url
        self.current_article = None

        # Control Bar (Top)
        self.controls = ttk.Frame(self, padding=5)
        self.controls.pack(fill="x")

        self.stay_open_var = tk.BooleanVar(value=True)
        self.stay_open_chk = ttk.Checkbutton(
            self.controls,
            text="Stay Open / On Top",
            variable=self.stay_open_var,
            command=self._update_window_behavior
        )
        self.stay_open_chk.pack(side="left", padx=10)

        self.nav_visible = True
        self.toggle_nav_btn = ttk.Button(
            self.controls,
            text="Hide Navigation",
            command=self.toggle_nav
        )
        self.toggle_nav_btn.pack(side="left", padx=10)

        # Content Editor Button
        self.edit_btn = ttk.Button(
            self.controls,
            text="Edit Content",
            command=self._open_editor
        )
        if self.enable_editor:
            self.edit_btn.pack(side="left", padx=10)

        # Update Notification (Hidden by default)
        self.update_frame = ttk.Frame(self.controls)
        self.update_label = ttk.Label(
            self.update_frame,
            text="Update available!",
            foreground="orange",
            font=("Segoe UI", 9, "bold")
        )
        self.update_label.pack(side="left", padx=5)
        self.reload_btn = ttk.Button(
            self.update_frame,
            text="Reload",
            command=self.refresh_list,
            style="Accent.TButton"
        )
        self.reload_btn.pack(side="left", padx=5)

        # Use PanedWindow for resizable side-by-side layout
        self.paned = ttk.PanedWindow(self, orient="horizontal")
        self.paned.pack(fill="both", expand=True)

        # Left side: Navigation
        self.nav_frame = NavFrame(self.paned, on_select=self._on_article_selected)
        self.paned.add(self.nav_frame, weight=1)

        # Right side: Content
        self.viewer = ArticleViewer(self.paned, content_manager=self.content_manager,
                                    on_link_click=self._on_link_clicked)
        self.paned.add(self.viewer, weight=4)

        # Load initial content
        self.refresh_list()
        self._load_default_article()

        # Initial behavior
        self._update_window_behavior()

        # Start background update check
        from help_window.utils.config import get_role
        if get_role() == "subscriber":
            from help_window.sync_manager import SyncManager
            self.sync_manager = SyncManager(self.content_manager.content_dir,
                                            on_update_available=self._on_sync_update,
                                            server_url=self.server_url)
            self.sync_manager.start()
        else:
            self.after(5000, self._check_for_content_updates)

    def _on_sync_update(self, new_hash):
        """Callback when SyncManager finds a verified update in staging."""
        self.after(0, lambda: self.update_frame.pack(side="left", padx=20))

    def _check_for_content_updates(self):
        """Periodically checks for content updates on disk."""
        try:
            if self.content_manager.check_for_updates():
                self.update_frame.pack(side="left", padx=20)
        except Exception as e:
            import logging
            logging.getLogger(__name__).error(f"Error checking for updates: {e}")

        # Check again in 30 seconds
        self.after(30000, self._check_for_content_updates)

    def toggle_nav(self):
        """Toggles the visibility of the navigation sidebar."""
        if self.nav_visible:
            self.paned.forget(self.nav_frame)
            self.toggle_nav_btn.configure(text="Show Navigation")
            self.nav_visible = False
        else:
            self.paned.insert(0, self.nav_frame, weight=1)
            self.toggle_nav_btn.configure(text="Hide Navigation")
            self.nav_visible = True

    def _update_window_behavior(self):
        """Updates stay-on-top and focus-out behavior based on 'Stay Open' setting."""
        from dev_common import window_topmost

        root = self.winfo_toplevel()
        if self.stay_open_var.get():
            window_topmost(root, set_to=True)
            root.unbind("<FocusOut>")
        else:
            window_topmost(root, set_to=False)
            # Close window when it loses focus
            # We use a delay to avoid closing when focus moves to a child widget
            root.bind("<FocusOut>", self._on_focus_out)

    def _on_focus_out(self, event):
        """Handles focus loss."""
        # We use a small delay to see where the focus went
        self.after(200, self._check_focus)

    def _check_focus(self):
        """Actual check for focus loss."""
        try:
            root = self.winfo_toplevel()
            if not root.winfo_exists():
                return

            focused = root.focus_get()
            if focused is None:
                # Focus went to another application
                root.destroy()
        except Exception:
            pass

    def refresh_list(self):
        """Refreshes the article list from the content manager."""
        if hasattr(self, 'sync_manager'):
            self.sync_manager.apply_update()
            self.content_manager.manifest = self.content_manager._load_manifest()

        articles = self.content_manager.scan_content(force=True)
        self.nav_frame.populate(articles)
        self.update_frame.pack_forget()
        self.content_manager.save_cache()

        # Reload current article if it was changed
        if self.current_article:
            path = self.current_article.get("file_path")
            updated_meta = next((a for a in articles if a.get("file_path") == path), None)
            if updated_meta:
                self.nav_frame.select_article(path)
                self._on_article_selected(updated_meta)

    def _open_editor(self):
        """Opens the help content editor."""
        from help_window.editor.editor_manager import EditorManager
        EditorManager(self, self.content_manager, live_viewer=self.viewer)

    def _on_article_selected(self, article_meta: Dict):
        """Callback when an article is selected in the NavFrame."""
        self.current_article = article_meta
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

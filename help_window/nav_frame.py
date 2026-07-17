import tkinter as tk
from tkinter import ttk
from typing import List, Dict, Callable


class NavFrame(ttk.Frame):
    """
    Navigation sidebar for help articles.
    Displays articles grouped by sections with large, touchscreen-friendly buttons.
    """

    def __init__(self, parent, on_select: Callable[[Dict], None], **kwargs):
        super().__init__(parent, **kwargs)
        self.on_select = on_select
        self.current_selection = None
        self.buttons = {}  # Store buttons to allow highlighting

        # Scrollable area for the list
        self.canvas = tk.Canvas(self, highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        # Handle mouse wheel scrolling
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def populate(self, articles: List[Dict]):
        """
        Populates the navigation list from a list of article metadata.
        """
        # Clear existing content
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        self.buttons = {}

        current_section = None

        for article in articles:
            section = article.get("section", "")
            if section != current_section:
                current_section = section
                if current_section:
                    # Add section header
                    header = ttk.Label(
                        self.scrollable_frame,
                        text=current_section.upper(),
                        font=("Segoe UI", 10, "bold"),
                        padding=(10, 15, 10, 5)
                    )
                    header.pack(fill="x")
                else:
                    # Root section
                    header = ttk.Label(
                        self.scrollable_frame,
                        text="GENERAL",
                        font=("Segoe UI", 10, "bold"),
                        padding=(10, 15, 10, 5)
                    )
                    header.pack(fill="x")

            # Create article button
            title = article.get("title", "Untitled")
            if article.get("is_broken"):
                title = f"⚠ {title} (Broken)"

            # Using a Label or Button? 
            # Buttons in Azure theme have specific styles. 
            # For touchscreen, a large label with padding might be better or a custom style button.
            btn = ttk.Button(
                self.scrollable_frame,
                text=title,
                command=lambda a=article: self._handle_click(a),
                style="Nav.TButton"  # We will define this style if needed, or use default
            )
            # In Azure theme, 'Toggle.TButton' might be useful but we want a radio-like behavior

            btn.pack(fill="x", padx=5, pady=2)
            self.buttons[article["file_path"]] = btn

    def _handle_click(self, article: Dict):
        self.select_article(article["file_path"])
        if self.on_select:
            self.on_select(article)

    def select_article(self, file_path: str):
        """Highlights the selected article and un-highlights others."""
        # Visual feedback for selection
        if self.current_selection and self.current_selection in self.buttons:
            # Reset style of previous
            self.buttons[self.current_selection].configure(style="TButton")

        self.current_selection = file_path
        if file_path in self.buttons:
            # Highlight current
            self.buttons[file_path].configure(style="Accent.TButton")

            # Ensure it's visible in the scrollable area
            # (Simplistic implementation)
            # self.canvas.see(self.buttons[file_path]) # Canvas doesn't have 'see'

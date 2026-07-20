import os
import tkinter as tk
from tkinter import ttk
from typing import List, Dict, Callable

from PIL import Image, ImageTk

from .utils.path_utils import resolve_resource_path
from .utils.scaling import calculate_dimensions
from .widgets.video_player import HelpVideoPlayer


class ArticleViewer(ttk.Frame):
    """
    A widget to display articles with mixed text and images.
    Refined for the Help Window with support for internal links.
    """

    def __init__(self, parent, on_link_click: Callable[[str], None] = None, **kwargs):
        super().__init__(parent, **kwargs)
        self.on_link_click = on_link_click

        # Title label above the content
        self.title_var = tk.StringVar(value="")
        self.title_label = ttk.Label(
            self,
            textvariable=self.title_var,
            font=("Segoe UI", 20, "bold"),
            padding=(20, 10)
        )
        self.title_label.pack(fill="x")

        # Create the Text widget and Scrollbar
        self.text_area = tk.Text(
            self,
            wrap="word",
            padx=20,
            pady=10,
            font=("Segoe UI", 11),
            cursor="arrow",
            state="disabled",
            borderwidth=0,
            highlightthickness=0
        )
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.text_area.yview)
        self.text_area.configure(yscrollcommand=self.scrollbar.set)

        # Layout
        self.scrollbar.pack(side="right", fill="y")
        self.text_area.pack(side="left", fill="both", expand=True)

        # Define styles (tags)
        self.text_area.tag_configure("header", font=("Segoe UI", 16, "bold"), spacing1=10, spacing3=10)
        self.text_area.tag_configure("subheader", font=("Segoe UI", 13, "bold"), spacing1=10, spacing3=5)
        self.text_area.tag_configure("paragraph", font=("Segoe UI", 11), spacing1=5, spacing3=5)
        self.text_area.tag_configure("center", justify="center")
        self.text_area.tag_configure("link", foreground="#0078d4", underline=True)

        # Link hover cursor
        self.text_area.tag_bind("link", "<Enter>", lambda e: self.text_area.config(cursor="hand2"))
        self.text_area.tag_bind("link", "<Leave>", lambda e: self.text_area.config(cursor="arrow"))

        self._media_elements = []  # List of dicts: {"type": "image"|"video", "widget": widget, "path": path, "metadata": metadata}
        self._images = []  # Keep references to PhotoImage objects
        self._videos = []  # Keep references to video players

        self.text_area.bind("<Configure>", self._on_text_area_configure)
        self._resize_timer = None

    def load_article(self, title: str, article_data: List[Dict[str, str]]):
        """
        Loads an article.
        """
        self.title_var.set(title)
        self.clear()
        self.text_area.configure(state="normal")

        for block in article_data:
            block_type = block.get("type")
            content = block.get("content", "")

            if block_type == "header":
                # We already have a main title label, but if there are headers in content:
                self.text_area.insert("end", content + "\n", "header")
            elif block_type == "subheader":
                self.text_area.insert("end", content + "\n", "subheader")
            elif block_type == "paragraph":
                # Check for links in paragraph? 
                # For now assume simple paragraph. 
                # Phase 3 will handle complex linking.
                self.text_area.insert("end", content + "\n", "paragraph")
            elif block_type == "image":
                self._add_image(content, block)
            elif block_type == "video":
                self._add_video(content, block)
            elif block_type == "link":
                target = block.get("target", "")
                self._add_link(content, target)
            elif block_type == "separator":
                self.text_area.insert("end", "\n" + "-" * 40 + "\n\n", "center")

        self.text_area.configure(state="disabled")

    def _get_visible_width(self):
        """Returns the width of the text area minus padding."""
        self.update_idletasks()
        width = self.text_area.winfo_width()
        # Subtract padding
        return max(10, width - 60)

    def _calculate_dimensions(self, orig_w, orig_h, metadata):
        """Calculates target dimensions using utility function."""
        viewer_width = self._get_visible_width()
        return calculate_dimensions(viewer_width, orig_w, orig_h, metadata)

    def _on_text_area_configure(self, event):
        """Debounced resize handler."""
        if self._resize_timer:
            self.after_cancel(self._resize_timer)
        self._resize_timer = self.after(200, self._apply_responsive_scaling)

    def _apply_responsive_scaling(self):
        """Re-scales all media elements to fit the current window width."""
        for element in self._media_elements:
            if element["type"] == "image":
                self._rescale_image(element)
            elif element["type"] == "video":
                self._rescale_video(element)

    def _rescale_image(self, element):
        try:
            with Image.open(element["path"]) as img:
                orig_w, orig_h = img.size
                target_w, target_h = self._calculate_dimensions(orig_w, orig_h, element["metadata"])

                # Resize
                resized_img = img.resize((target_w, target_h), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(resized_img)

                # Update widget
                element["widget"].configure(image=photo)
                # Keep reference
                element["photo"] = photo
        except Exception as e:
            print(f"Error rescaling image: {e}")

    def _rescale_video(self, element):
        try:
            video_player = element["widget"]
            metadata = element["metadata"]

            info = video_player.get_video_info()
            orig_w, orig_h = info.get("dimensions", (640, 360))

            target_w, target_h = self._calculate_dimensions(orig_w, orig_h, metadata)
            video_player.update_display_size(target_w, target_h)
        except Exception as e:
            print(f"Error rescaling video: {e}")

    def _add_image(self, image_path: str, metadata: dict):
        """Internal method to add an image."""
        resolved_path = resolve_resource_path(image_path)
        if not os.path.isfile(resolved_path):
            self.text_area.insert("end", f"\n[Image not found: {image_path}]\n", "paragraph")
            return

        try:
            with Image.open(resolved_path) as img:
                orig_w, orig_h = img.size
                target_w, target_h = self._calculate_dimensions(orig_w, orig_h, metadata)

                # Resize
                resized_img = img.resize((target_w, target_h), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(resized_img)

                # Use a Label to display the image
                label = ttk.Label(self.text_area, image=photo)

                # Keep references
                self._images.append(photo)
                element = {
                    "type": "image",
                    "widget": label,
                    "path": resolved_path,
                    "metadata": metadata,
                    "photo": photo
                }
                self._media_elements.append(element)

                self.text_area.insert("end", "\n")
                self.text_area.window_create("end", window=label)
                self.text_area.insert("end", "\n\n")

                line_index = self.text_area.index("end-2c").split('.')[0]
                self.text_area.tag_add("center", f"{line_index}.0", f"{line_index}.end")
        except Exception as e:
            self.text_area.insert("end", f"\n[Error loading image: {e}]\n", "paragraph")

    def _add_video(self, video_path: str, metadata: dict):
        """Internal method to add a video player."""
        resolved_path = resolve_resource_path(video_path)
        if not os.path.isfile(resolved_path):
            self.text_area.insert("end", f"\n[Video not found: {video_path}]\n", "paragraph")
            return

        try:
            video_player = HelpVideoPlayer(self.text_area, resolved_path)
            
            # Initial size calculation
            target_w, target_h = self._calculate_dimensions(640, 360, metadata)
            video_player.update_display_size(target_w, target_h)

            # Keep reference
            self._videos.append(video_player)
            self._media_elements.append({
                "type": "video",
                "widget": video_player,
                "metadata": metadata
            })

            # When duration is loaded, rescale again to get correct aspect ratio
            video_player.bind("<<VideoDurationLoaded>>", lambda e: self._rescale_video(self._media_elements[-1]))

            # Embed in text area
            self.text_area.insert("end", "\n")
            self.text_area.window_create("end", window=video_player)
            self.text_area.insert("end", "\n\n")

            # Center it
            line_index = self.text_area.index("end-2c").split('.')[0]
            self.text_area.tag_add("center", f"{line_index}.0", f"{line_index}.end")

        except Exception as e:
            self.text_area.insert("end", f"\n[Error loading video: {e}]\n", "paragraph")

    def _add_link(self, text: str, target: str):
        """Adds a clickable link."""
        tag_name = f"link_{target.replace('.', '_').replace('/', '_')}"
        self.text_area.insert("end", text + "\n", ("link", tag_name))
        if self.on_link_click:
            self.text_area.tag_bind(tag_name, "<Button-1>", lambda e, t=target: self.on_link_click(t))

    def clear(self):
        self.text_area.configure(state="normal")
        self.text_area.delete("1.0", "end")
        self.text_area.configure(state="disabled")

        # Stop all video players before clearing
        for player in self._videos:
            try:
                player.stop()
            except:
                pass
        
        self._images = []
        self._videos = []
        self._media_elements = []

import os
import tkinter as tk
from tkinter import ttk
from typing import List, Dict, Callable


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
        self._images = []  # Keep references
        self._videos = []  # Keep references to video players

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
                self._add_image(content)
            elif block_type == "video":
                self._add_video(content)
            elif block_type == "link":
                target = block.get("target", "")
                self._add_link(content, target)
            elif block_type == "separator":
                self.text_area.insert("end", "\n" + "-" * 40 + "\n\n", "center")

        self.text_area.configure(state="disabled")

    def _add_image(self, image_path: str):
        """Internal method to add an image."""
        if not image_path:
            self.text_area.insert("end", "\n[Error: Image path is empty]\n", "paragraph")
            return

        # Check if the path exists and is a file
        if not os.path.isfile(image_path):
            # If not an absolute path, try relative to project root (CWD)
            if not os.path.isabs(image_path):
                abs_path = os.path.abspath(os.path.join(os.getcwd(), image_path))
                if os.path.isfile(abs_path):
                    image_path = abs_path
                else:
                    self.text_area.insert("end", f"\n[Image not found: {image_path}]\n", "paragraph")
                    return
            else:
                # Absolute path provided but not found/not a file
                self.text_area.insert("end", f"\n[Image not found: {image_path}]\n", "paragraph")
                return

        try:
            img = tk.PhotoImage(file=image_path)
            self._images.append(img)
            self.text_area.insert("end", "\n")
            self.text_area.image_create("end", image=img)
            self.text_area.insert("end", "\n\n")

            line_index = self.text_area.index("end-2c").split('.')[0]
            self.text_area.tag_add("center", f"{line_index}.0", f"{line_index}.end")
        except Exception as e:
            self.text_area.insert("end", f"\n[Error loading image: {e}]\n", "paragraph")

    def _add_video(self, video_path: str):
        """Internal method to add a video player."""
        if not video_path:
            self.text_area.insert("end", "\n[Error: Video path is empty]\n", "paragraph")
            return

        # Check if the path exists and is a file
        if not os.path.isfile(video_path):
            if not os.path.isabs(video_path):
                abs_path = os.path.abspath(os.path.join(os.getcwd(), video_path))
                if os.path.isfile(abs_path):
                    video_path = abs_path
                else:
                    self.text_area.insert("end", f"\n[Video not found: {video_path}]\n", "paragraph")
                    return
            else:
                self.text_area.insert("end", f"\n[Video not found: {video_path}]\n", "paragraph")
                return

        try:
            from tkVideoPlayer import TkinterVideo

            # Container frame for video and controls
            container = ttk.Frame(self.text_area)

            # Player
            # scaled=True ensures it fits the frame
            player = TkinterVideo(master=container, scaled=True)
            player.load(video_path)
            player.set_size((400, 300))  # Default size for inline video
            player.pack(expand=True, fill="both", padx=5, pady=5)

            # Controls frame
            controls = ttk.Frame(container)
            controls.pack(fill="x", side="bottom")

            def toggle_play():
                if player.is_paused():
                    player.play()
                    play_btn.configure(text="Pause")
                else:
                    player.pause()
                    play_btn.configure(text="Play")

            play_btn = ttk.Button(controls, text="Play", command=toggle_play)
            play_btn.pack(side="left", padx=5)

            def stop_video():
                player.stop()
                play_btn.configure(text="Play")
                progress_var.set(0)

            stop_btn = ttk.Button(controls, text="Stop", command=stop_video)
            stop_btn.pack(side="left", padx=5)

            # Progress slider
            progress_var = tk.DoubleVar()

            def seek_video(value):
                # Only seek if not triggered by the update loop
                if not getattr(player, "_updating_slider", False):
                    player.seek(int(float(value)))

            slider = ttk.Scale(controls, from_=0, to=0, variable=progress_var, orient="horizontal", command=seek_video)
            slider.pack(side="left", fill="x", expand=True, padx=5)

            def update_duration(event):
                duration = player.video_info()["duration"]
                slider.configure(to=duration)

            def update_scale(event):
                player._updating_slider = True
                curr_dur = player.current_duration()
                progress_var.set(curr_dur)
                player._updating_slider = False

            def video_ended(event):
                play_btn.configure(text="Play")
                progress_var.set(0)

            player.bind("<<Duration>>", update_duration)
            player.bind("<<SecondChanged>>", update_scale)
            player.bind("<<Ended>>", video_ended)

            # Keep reference
            self._videos.append(player)

            # Embed in text area
            self.text_area.insert("end", "\n")
            self.text_area.window_create("end", window=container)
            self.text_area.insert("end", "\n\n")

            # Center it
            line_index = self.text_area.index("end-2c").split('.')[0]
            self.text_area.tag_add("center", f"{line_index}.0", f"{line_index}.end")

        except ImportError:
            self.text_area.insert("end", "\n[Error: tkVideoPlayer not installed]\n", "paragraph")
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

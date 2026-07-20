import os
import tkinter as tk
from tkinter import ttk
from typing import List, Dict, Callable

from PIL import Image, ImageTk


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
        """Calculates target dimensions based on metadata and viewer width."""
        viewer_width = self._get_visible_width()

        target_w = None
        target_h = None

        # 1. Check size presets
        size_presets = {
            "thumbnail": 0.25,
            "small": 0.50,
            "medium": 0.75,
            "large": 0.90,
            "fill": 1.0
        }

        size = metadata.get("size")
        if size in size_presets:
            target_w = viewer_width * size_presets[size]

        # 2. Check width_pct
        width_pct = metadata.get("width_pct")
        if width_pct is not None:
            try:
                target_w = viewer_width * (float(width_pct) / 100.0)
            except ValueError:
                pass

        # 3. Check static width/height
        # Format "1441x1080"
        static_size = metadata.get("width")
        if isinstance(static_size, str) and "x" in static_size:
            try:
                w, h = map(int, static_size.split("x"))
                target_w = w
                target_h = h
            except ValueError:
                pass
        elif metadata.get("width") and metadata.get("height"):
            try:
                target_w = int(metadata.get("width"))
                target_h = int(metadata.get("height"))
            except ValueError:
                pass

        # Default: use original size but capped at viewer width
        if target_w is None:
            target_w = orig_w

        # HLP-015: Responsive Scaling - MUST fit within viewer width
        if target_w > viewer_width:
            target_w = viewer_width

        # Maintain aspect ratio if height not explicitly set
        if target_h is None:
            ratio = target_w / orig_w
            target_h = orig_h * ratio

        return int(target_w), int(target_h)

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
            player = element["player"]
            container = element["widget"]
            controls = element["controls"]
            metadata = element["metadata"]

            info = player.video_info()
            orig_w, orig_h = info.get("dimensions", (640, 360))

            target_w, target_h = self._calculate_dimensions(orig_w, orig_h, metadata)

            # Update player internal size
            player.set_size((target_w, target_h))

            # Update container size to fit both player and controls
            # Measure controls height (reqheight is better for non-rendered widgets)
            controls_h = controls.winfo_reqheight()
            if controls_h < 10:
                controls_h = 40  # sensible default for buttons + slider

            # The container should be large enough for the video and the controls
            # We add some padding to account for padx/pady
            container.configure(width=target_w + 10, height=target_h + controls_h + 20)
            container.pack_propagate(False)

        except Exception as e:
            print(f"Error rescaling video: {e}")

    def _add_image(self, image_path: str, metadata: dict):
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
            with Image.open(image_path) as img:
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
                    "path": image_path,
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

            # Controls frame
            controls = ttk.Frame(container)
            controls.pack(fill="x", side="bottom", padx=5, pady=5)

            # Player
            # scaled=True ensures it fits the frame
            player = TkinterVideo(master=container, scaled=True)
            player.load(video_path)

            # Initial size calculation
            target_w, target_h = self._calculate_dimensions(640, 360, metadata)
            player.set_size((target_w, target_h))
            player.pack(expand=True, fill="both", side="top", padx=5, pady=5)

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
                info = player.video_info()
                duration = info["duration"]
                slider.configure(to=duration)

                # Re-calculate size based on actual video dimensions if available
                orig_w, orig_h = info.get("dimensions", (640, 360))
                self._rescale_video({
                    "player": player,
                    "widget": container,
                    "controls": controls,
                    "metadata": metadata,
                    "type": "video"
                })

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
            self._media_elements.append({
                "type": "video",
                "player": player,
                "widget": container,
                "controls": controls,
                "metadata": metadata
            })

            # Force initial scaling
            self._rescale_video(self._media_elements[-1])

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
        self._media_elements = []

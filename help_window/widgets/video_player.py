import tkinter as tk
from tkinter import ttk
from typing import Dict, Any


class HelpVideoPlayer(ttk.Frame):
    """
    A standalone video player widget for the Help Window.
    Encapsulates tkVideoPlayer and its controls.
    """

    def __init__(self, parent, video_path: str, metadata: dict = None, **kwargs):
        super().__init__(parent, **kwargs)
        self.video_path = video_path
        self.metadata = metadata or {}
        self._updating_slider = False

        # Controls frame at the bottom
        self.controls = ttk.Frame(self)
        self.controls.pack(fill="x", side="bottom", padx=5, pady=5)

        try:
            from tkVideoPlayer import TkinterVideo

            # Player - scaled=True ensures it fits the frame
            self.player = TkinterVideo(master=self, scaled=True)
            self.player.load(video_path)
            self.player.pack(expand=True, fill="both", side="top", padx=5, pady=5)

            # Play/Pause button
            self.play_btn = ttk.Button(self.controls, text="Play", command=self.toggle_play)
            self.play_btn.pack(side="left", padx=5)

            # Stop button
            self.stop_btn = ttk.Button(self.controls, text="Stop", command=self.stop_video)
            self.stop_btn.pack(side="left", padx=5)

            # Progress slider
            self.progress_var = tk.DoubleVar()
            self.slider = ttk.Scale(
                self.controls,
                from_=0,
                to=0,
                variable=self.progress_var,
                orient="horizontal",
                command=self.seek_video
            )
            self.slider.pack(side="left", fill="x", expand=True, padx=5)

            # Events
            self.player.bind("<<Duration>>", self._update_duration)
            self.player.bind("<<SecondChanged>>", self._update_scale)
            self.player.bind("<<Ended>>", self._video_ended)

        except ImportError:
            error_label = ttk.Label(self, text="[Error: tkVideoPlayer not installed]")
            error_label.pack(pady=20)
            self.player = None

    def toggle_play(self):
        if not self.player: return
        if self.player.is_paused():
            self.player.play()
            self.play_btn.configure(text="Pause")
        else:
            self.player.pause()
            self.play_btn.configure(text="Play")

    def stop_video(self):
        if not self.player: return
        self.player.stop()
        self.play_btn.configure(text="Play")
        self.progress_var.set(0)

    def seek_video(self, value):
        if not self.player: return
        if not self._updating_slider:
            self.player.seek(int(float(value)))

    def _update_duration(self, event):
        if not self.player: return
        info = self.player.video_info()
        duration = info["duration"]
        self.slider.configure(to=duration)
        # Notify listeners that duration is loaded (important for initial scaling)
        self.event_generate("<<VideoDurationLoaded>>")

    def _update_scale(self, event):
        if not self.player: return
        self._updating_slider = True
        curr_dur = self.player.current_duration()
        self.progress_var.set(curr_dur)
        self._updating_slider = False

    def _video_ended(self, event):
        self.play_btn.configure(text="Play")
        self.progress_var.set(0)

    def update_display_size(self, viewer_width: int):
        """Updates the size of the player based on viewer width and metadata."""
        if not self.player: return

        from ..utils.scaling import calculate_dimensions
        info = self.player.video_info()
        orig_w, orig_h = info.get("dimensions", (640, 360))

        target_w, target_h = calculate_dimensions(viewer_width, orig_w, orig_h, self.metadata)
        
        self.player.set_size((target_w, target_h))

        # Measure controls height
        controls_h = self.controls.winfo_reqheight()
        if controls_h < 10:
            controls_h = 40  # fallback

        self.configure(width=target_w + 10, height=target_h + controls_h + 20)
        self.pack_propagate(False)

    def get_video_info(self) -> Dict[str, Any]:
        if not self.player: return {}
        return self.player.video_info()

    def stop(self):
        """Stops playback and releases resources if needed."""
        if self.player:
            try:
                self.player.stop()
            except:
                pass

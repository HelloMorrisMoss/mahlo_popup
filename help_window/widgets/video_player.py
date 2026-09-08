import os
import queue
import threading
import time
import tkinter as tk
from tkinter import ttk
from typing import Dict, Any, Optional

from PIL import Image, ImageTk

try:
    import cv2
except ImportError:
    cv2 = None

from help_window import lg


class OpenCVVideoPlayer(ttk.Frame):
    """
    A video player using OpenCV as the backend.
    Supports 32-bit Windows 7 where PyAV/FFmpeg might be unavailable.
    """

    def __init__(self, parent, video_path: str, metadata: dict = None, **kwargs):
        super().__init__(parent, **kwargs)
        self.video_path = video_path
        self.metadata = metadata or {}

        self.cap = None
        self.fps = 30
        self.frame_count = 0
        self.duration = 0
        self.current_frame_idx = 0
        self._playing = False
        self._stop_thread = False
        self._seek_requested: Optional[int] = None

        self.frame_queue = queue.Queue(maxsize=10)
        self.display_label = ttk.Label(self)
        self.display_label.pack(expand=True, fill="both", side="top", padx=5, pady=5)

        # Controls frame
        self.controls = ttk.Frame(self)
        self.controls.pack(fill="x", side="bottom", padx=5, pady=5)

        self.play_btn = ttk.Button(self.controls, text="Play", command=self.toggle_play)
        self.play_btn.pack(side="left", padx=5)

        self.stop_btn = ttk.Button(self.controls, text="Stop", command=self.stop_video)
        self.stop_btn.pack(side="left", padx=5)

        self.progress_var = tk.DoubleVar()
        self.slider = ttk.Scale(
            self.controls,
            from_=0,
            to=100,
            variable=self.progress_var,
            orient="horizontal",
            command=self.request_seek
        )
        self.slider.pack(side="left", fill="x", expand=True, padx=5)

        self._last_photo = None
        self._target_size = (640, 360)

        if cv2:
            self.load_video()
        else:
            self.display_label.configure(text="[Error: OpenCV (cv2) not installed]")

    def load_video(self):
        self.cap = cv2.VideoCapture(self.video_path)
        if not self.cap.isOpened():
            self.display_label.configure(text=f"[Error: Could not open video {os.path.basename(self.video_path)}]")
            return

        self.fps = self.cap.get(cv2.CAP_PROP_FPS)
        if self.fps <= 0: self.fps = 30
        self.frame_count = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        self.duration = self.frame_count / self.fps

        self.slider.configure(to=self.frame_count)

        # Start reading thread
        self._stop_thread = False
        self.thread = threading.Thread(target=self._read_frames, daemon=True)
        self.thread.start()

        # Start UI update loop
        self.after(10, self._update_ui)

        # Initial frame
        self.request_seek(0)

        # Notify ArticleViewer that duration is available
        self.event_generate("<<VideoDurationLoaded>>")

    def _read_frames(self):
        while not self._stop_thread:
            if self._seek_requested is not None:
                frame_idx = self._seek_requested
                self._seek_requested = None
                self.cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
                self.current_frame_idx = frame_idx
                # Clear queue on seek
                while not self.frame_queue.empty():
                    try:
                        self.frame_queue.get_nowait()
                    except queue.Empty:
                        break

            if self._playing or not self.frame_queue.full():
                ret, frame = self.cap.read()
                if ret:
                    self.current_frame_idx += 1
                    # Convert BGR to RGB
                    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

                    if not self.frame_queue.full():
                        self.frame_queue.put((self.current_frame_idx, frame))

                    if self._playing:
                        time.sleep(1.0 / self.fps)
                else:
                    if self._playing:
                        self._playing = False
                        self.event_generate("<<Ended>>")
                    time.sleep(0.1)
            else:
                time.sleep(0.1)

    def _update_ui(self):
        if self._stop_thread: return

        try:
            while not self.frame_queue.empty():
                idx, frame = self.frame_queue.get_nowait()

                # Resize
                img = Image.fromarray(frame)
                img = img.resize(self._target_size, Image.Resampling.LANCZOS)

                photo = ImageTk.PhotoImage(image=img)
                self.display_label.configure(image=photo)
                self._last_photo = photo  # Keep reference

                if not self.slider.winfo_viewable() or not self._playing:  # only update slider if not manually seeking
                    self.progress_var.set(idx)
        except queue.Empty:
            pass

        self.after(int(1000 / self.fps), self._update_ui)

    def toggle_play(self):
        self._playing = not self._playing
        self.play_btn.configure(text="Pause" if self._playing else "Play")

    def stop_video(self):
        self._playing = False
        self.play_btn.configure(text="Play")
        self.request_seek(0)

    def request_seek(self, value):
        self._seek_requested = int(float(value))
        self.progress_var.set(self._seek_requested)

    def update_display_size(self, viewer_width: int):
        from ..utils.scaling import calculate_dimensions

        orig_w = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)) if self.cap else 640
        orig_h = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)) if self.cap else 360

        target_w, target_h = calculate_dimensions(viewer_width, orig_w, orig_h, self.metadata)
        self._target_size = (target_w, target_h)

        controls_h = self.controls.winfo_reqheight() or 40
        self.configure(width=target_w + 10, height=target_h + controls_h + 20)
        self.pack_propagate(False)

    def video_info(self) -> dict:
        if not self.cap: return {"duration": 0, "dimensions": (640, 360)}
        return {
            "duration": self.duration,
            "dimensions": (int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
                           int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)))
        }

    def stop(self):
        self._stop_thread = True
        if self.cap:
            self.cap.release()


class HelpVideoPlayer(ttk.Frame):
    """
    A standalone video player widget for the Help Window.
    Encapsulates a video backend (tkVideoPlayer or OpenCV) and its controls.
    """

    def __init__(self, parent, video_path: str, metadata: dict = None, **kwargs):
        super().__init__(parent, **kwargs)
        self.video_path = video_path
        self.metadata = metadata or {}

        # Choose backend
        # 32-bit Win7 check (simplified)
        import platform
        import struct
        is_32bit_win7 = (platform.system() == "Windows" and
                         platform.release() == "7" and
                         struct.calcsize("P") == 4)

        self.player = None

        if is_32bit_win7 or not self._has_tkvideoplayer():
            lg.info(f"Using OpenCV backend for video: {video_path}")
            self.player = OpenCVVideoPlayer(self, video_path, metadata)
        else:
            lg.info(f"Using tkVideoPlayer backend for video: {video_path}")
            self.player = self._init_tkvideoplayer(video_path, metadata)

        if self.player:
            self.player.pack(expand=True, fill="both")
            # Forward events
            self.player.bind("<<VideoDurationLoaded>>", lambda e: self.event_generate("<<VideoDurationLoaded>>"))
            self.player.bind("<<Ended>>", lambda e: self.event_generate("<<Ended>>"))

    def _has_tkvideoplayer(self):
        try:
            from tkVideoPlayer import TkinterVideo
            return True
        except ImportError:
            return False

    def _init_tkvideoplayer(self, video_path, metadata):
        # We need to wrap the old implementation or just use it here
        return LegacyHelpVideoPlayer(self, video_path, metadata)

    def toggle_play(self):
        if self.player: self.player.toggle_play()

    def stop_video(self):
        if self.player: self.player.stop_video()

    def update_display_size(self, viewer_width: int):
        if self.player: self.player.update_display_size(viewer_width)

    def get_video_info(self) -> Dict[str, Any]:
        if not self.player: return {}
        if hasattr(self.player, "video_info"):
            return self.player.video_info()
        return self.player.get_video_info()  # for legacy

    def stop(self):
        if self.player: self.player.stop()


class LegacyHelpVideoPlayer(ttk.Frame):
    """Original implementation using tkVideoPlayer."""
    def __init__(self, parent, video_path: str, metadata: dict = None, **kwargs):
        super().__init__(parent, **kwargs)
        self.video_path = video_path
        self.metadata = metadata or {}
        self._updating_slider = False

        self.controls = ttk.Frame(self)
        self.controls.pack(fill="x", side="bottom", padx=5, pady=5)

        from tkVideoPlayer import TkinterVideo
        self.player = TkinterVideo(master=self, scaled=True)
        self.player.load(video_path)
        self.player.pack(expand=True, fill="both", side="top", padx=5, pady=5)

        self.play_btn = ttk.Button(self.controls, text="Play", command=self.toggle_play)
        self.play_btn.pack(side="left", padx=5)

        self.stop_btn = ttk.Button(self.controls, text="Stop", command=self.stop_video)
        self.stop_btn.pack(side="left", padx=5)

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

        self.player.bind("<<Duration>>", self._update_duration)
        self.player.bind("<<SecondChanged>>", self._update_scale)
        self.player.bind("<<Ended>>", self._video_ended)

    def toggle_play(self):
        if self.player.is_paused():
            self.player.play()
            self.play_btn.configure(text="Pause")
        else:
            self.player.pause()
            self.play_btn.configure(text="Play")

    def stop_video(self):
        self.player.stop()
        self.play_btn.configure(text="Play")
        self.progress_var.set(0)

    def seek_video(self, value):
        if not self._updating_slider:
            self.player.seek(int(float(value)))

    def _update_duration(self, event):
        info = self.player.video_info()
        duration = info["duration"]
        self.slider.configure(to=duration)
        self.event_generate("<<VideoDurationLoaded>>")

    def _update_scale(self, event):
        self._updating_slider = True
        curr_dur = self.player.current_duration()
        self.progress_var.set(curr_dur)
        self._updating_slider = False

    def _video_ended(self, event):
        self.play_btn.configure(text="Play")
        self.progress_var.set(0)
        self.event_generate("<<Ended>>")

    def update_display_size(self, viewer_width: int):
        from ..utils.scaling import calculate_dimensions
        info = self.player.video_info()
        orig_w, orig_h = info.get("dimensions", (640, 360))
        target_w, target_h = calculate_dimensions(viewer_width, orig_w, orig_h, self.metadata)
        self.player.set_size((target_w, target_h))
        controls_h = self.controls.winfo_reqheight() or 40
        self.configure(width=target_w + 10, height=target_h + controls_h + 20)
        self.pack_propagate(False)

    def video_info(self) -> dict:
        return self.player.video_info()

    def stop(self):
        try:
            self.player.stop()
        except:
            pass

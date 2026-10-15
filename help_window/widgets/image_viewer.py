from tkinter import ttk

from PIL import Image, ImageTk

from ..utils.scaling import calculate_dimensions


class HelpImage(ttk.Label):
    """
    A self-scaling image widget for the ArticleViewer.
    Handles its own PhotoImage reference to prevent garbage collection.
    """

    def __init__(self, parent, image_path: str, metadata: dict, **kwargs):
        super().__init__(parent, **kwargs)
        self.image_path = image_path
        self.metadata = metadata
        self.photo = None

    def update_display_size(self, viewer_width: int):
        """Re-scales the image based on the available width."""
        try:
            with Image.open(self.image_path) as img:
                orig_w, orig_h = img.size
                target_w, target_h = calculate_dimensions(viewer_width, orig_w, orig_h, self.metadata)

                # Resize using high-quality resampling
                resized_img = img.resize((target_w, target_h), Image.Resampling.LANCZOS)
                self.photo = ImageTk.PhotoImage(resized_img)

                # Update the label
                self.configure(image=self.photo)
                return True
        except Exception as e:
            print(f"Error scaling image {self.image_path}: {e}")
            return False

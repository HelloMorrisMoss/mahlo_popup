from tkinter import ttk


class HelpFrame(ttk.Frame):
    """
    Main container for the Help Window UI.
    Contains NavFrame and ArticleViewer.
    """

    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)

        self.label = ttk.Label(self, text="Help Window Content (Coming Soon)")
        self.label.pack(expand=True, fill="both")

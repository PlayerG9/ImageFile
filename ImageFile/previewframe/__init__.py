from imports import *
from .previewhandler import PreviewHandler


class PreviewFrame(tk.LabelFrame):
    def __init__(self, master):
        """
        Args:
            master:
        """
        super().__init__(
            master=master,
            text=lang("Preview")
        )
        PreviewHandler(self).place(relwidth=1.0, relheight=1.0)

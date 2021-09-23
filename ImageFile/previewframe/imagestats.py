from imports import *


class ImageStats(tk.Frame):
    def __init__(self, master, image: Image.Image, data: sql.Row):
        super().__init__(master, relief=RIDGE, borderwidth=2)
        ttk.Separator(self, orient=VERTICAL).grid(row=0, column=1, rowspan=10, sticky=NS, padx=5)
        self.lbl_size = tk.Label(self, text=lang('Size: {}x{}').format(*image.size))
        self.lbl_size.grid(row=0, column=0, sticky=EW)
        self.lbl_filename = tk.Label(self, text=data['basename']+data['extension'])
        self.lbl_filename.grid(row=0, column=2, sticky=EW)
        self.lbl_filesize = tk.Label(self,text=lang("Filesize: {}").format(format_filesize(len(data['data']))))
        self.lbl_filesize.grid(row=1, column=0, sticky=EW)
        self.lbl_format = tk.Label(self, text=image.format_description)  # no translation
        self.lbl_format.grid(row=1, column=2, sticky=EW)
        if getattr(image, 'is_animated', False):
            lbl = tk.Label(self, text=lang('Frames: {}').format(image.n_frames))
            lbl.grid(row=2, column=0, sticky=EW)

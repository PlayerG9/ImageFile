from imports import *
from .imagepreview import ImageWidget


class FloatWindow(tk.Toplevel):
    def __init__(self, image: Image.Image):
        super().__init__()
        self.attributes('-toolwindow', True, '-topmost', True)
        self.focus_set()

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.factor = 1.0

        self.canvas = canvas = tk.Canvas(
            master=self,
            takefocus=False,
            confine=False,  # allow to scroll outside the scrollregion
            relief=FLAT
        )
        canvas.grid(row=0, column=0, sticky=NSEW)
        xscroll = AutoScrollbar(self, orient=HORIZONTAL, command=canvas.xview)
        xscroll.grid(row=1, column=0, sticky=EW)
        yscroll = AutoScrollbar(self, orient=VERTICAL, command=canvas.yview)
        yscroll.grid(row=0, column=1, sticky=NS)
        canvas.configure(xscrollcommand=xscroll.set, yscrollcommand=yscroll.set)
        canvas.bind('<Button-2>', lambda e: canvas.scan_mark(e.x, e.y))
        canvas.bind('<B2-Motion>', lambda e: canvas.scan_dragto(e.x, e.y, gain=1))
        canvas.bind('<MouseWheel>', self.scrollwheel)

        self.image = image = ImageWidget(canvas, image)
        image.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox('all')))
        image.bind('<Button-2>', lambda e: canvas.scan_mark(e.x, e.y))
        image.bind('<B2-Motion>', lambda e: canvas.scan_dragto(e.x, e.y, gain=1))
        image.bind('<MouseWheel>', self.scrollwheel)
        canvas.create_window(0, 0, window=image, anchor=NW, tags=('image',))

    def scrollwheel(self, event):
        print(event)
        img = self.image
        width, height = img.size
        if event.delta < 0:
            width *= 0.9
            height *= 0.9
        elif event.delta > 0:
            width *= 1.1
            height *= 1.1
        else:
            return
        width = max(img.orig[0] // 10, width)
        height = max(img.orig[1] // 10, height)
        self.image.resize(width, height)
        # print(self.factor)
        # self.canvas.scale('image', 0, 0, self.factor, self.factor)

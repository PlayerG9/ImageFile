from imports import *
from .imagewidget import ImageWidget
from .imagestats import ImageStats
# experimental feature disabled
# from .floatwindow import FloatWindow


class ImagePreview(tk.Frame):
    def __init__(self, master, rowid: int):
        """
        Args:
            master:
            rowid (int):
        """
        super().__init__(master)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        self.rowid = rowid
        self.data = data = self.load()
        self.text = data['basename'] + data['extension']
        stream = BytesIO(data['data'])
        stream.seek(0)
        stream.filename = data['basename'] + data['extension']
        self.image: Image.Image = Image.open(stream)
        del stream

        # disabled temporarily (could improve performance on bigger images)
        # self.image.thumbnail((self.winfo_screenwidth(), self.winfo_screenheight()))
        # self.imagetk: tk.PhotoImage = None

        self.factor = 0

        # Header for image-stats (size, name, etc)

        self.headerframe = headerframe = ImageStats(self, self.image, data)
        headerframe.grid(row=0, column=0, sticky=EW)
        self.lbl_faktor = tk.Label(headerframe)
        self.lbl_faktor.grid(row=3, column=0, sticky=EW)

        # Tags etc

        # print(f"{data['tags']=}", type(data['tags']))
        self.last_tags = data['tags']
        self.tags = TagEntry(self, tags=data['tags'])
        self.tags.grid(row=1, column=0, sticky=EW)
        self.bind('<Leave>', lambda e: self.save_tags())
        self.bind('<Destroy>', lambda e: self.save_tags())

        # Frame to display the image

        self.measureframe = tk.Frame(self)
        self.measureframe.grid(row=2, column=0, sticky=NSEW, padx=15, pady=15)  # litle offset for image-size indicators
        self.imageframe = imageframe = tk.Frame(self)
        imageframe.grid(row=2, column=0)  # grid not sticky to keep it centered
        # experimental feature disabled
        # tk.Button(self, text='🗔', font='15', command=lambda: FloatWindow(self.image)).grid(row=1, column=0, sticky=NW)
        xsep = ttk.Separator(imageframe, orient=HORIZONTAL)
        self.lbl_width = tk.Label(imageframe, relief=GROOVE, text=self.image.width)
        ysep = ttk.Separator(imageframe, orient=VERTICAL)
        self.lbl_height = tk.Label(imageframe, relief=GROOVE, text=self.image.height)

        self.lbl_image = ImageWidget(imageframe, self.image)
        # self.lbl_image = tk.Label(imageframe)
        self.measureframe.bind('<Configure>', self.resize_image)
        self.bind('<Configure>', self.resize_image)
        self.bind('<Visibility>', self.resize_image)

        xsep.grid(row=1, column=1, sticky=EW)
        self.lbl_width.grid(row=1, column=1)
        ysep.grid(row=0, column=0, sticky=NS)
        self.lbl_height.grid(row=0, column=0)
        self.lbl_image.grid(row=0, column=1, sticky=NSEW)

    def destroy(self):
        try: del self.image
        except AttributeError: pass
        # del self.imagetk
        try: del self.data
        except AttributeError: pass
        super().destroy()

    def load(self) -> sql.Row:
        connection = sql.connect(DATABASEPATH, detect_types=True)
        connection.row_factory = sql.Row
        connection.create_function('str', 1, str)
        try:
            QUERY = r'SELECT str(basename) as basename, extension, tags, data FROM images WHERE rowid = ? LIMIT 1'

            cursor = connection.execute(QUERY, [self.rowid])

            return cursor.fetchone()
        finally:
            connection.close()

    def save_tags(self):
        tags = self.tags.get_tags()
        if tags == self.last_tags: return
        connection = sql.connect(DATABASEPATH, detect_types=True)
        try:
            QUERY = 'UPDATE images SET tags = ? WHERE rowid = ?'

            connection.execute(QUERY, (tags, self.rowid))

            connection.commit()
        finally:
            connection.close()
        self.last_tags = tags

    def resize_image(self, _=None):
        """
        Args:
            _:
        """
        if not self.winfo_viewable(): return

        # nw = self.winfo_width()
        # nh = self.winfo_height() - self.headerframe.winfo_height() - self.tags.winfo_height()
        nw, nh = self.measureframe.winfo_width(), self.measureframe.winfo_height()
        img = self.image
        factor = 1
        while img.width // factor > nw or img.height // factor > nh:
            factor += 1

        if factor == self.factor: return  # no useless resizing

        self.lbl_faktor['text'] = lang('Factor: 1:{}').format(factor)
        self.factor = factor

        try: self.lbl_image.resize(img.width // factor, img.height // factor)
        except ValueError: pass  # invalid new size
        # resized = self.image.resize((img.width // factor, img.height // factor))
        # self.lbl_image.set_image(resized)
        # del self.imagetk  # delete old image
        # self.imagetk = ImageTk.PhotoImage(resized)
        # del resized
        # self.lbl_image['image'] = self.imagetk

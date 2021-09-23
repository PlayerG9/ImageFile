from imports import *
from previewframe.imagestats import ImageStats


class ExportFrame(tk.Frame):
    alwaysdestroy = True  # hint for previewhandler to destroy this widget instead of just hiding it

    def __init__(self, rowid):
        self.rowid = rowid
        super().__init__()
        self.data = self.load()
        self.filename = filename = self.data['basename'] + self.data['extension']
        EventHandler.invoke('<Show-Widget>', self, text=lang('Export - {}').format(filename))

        stream = BytesIO(self.data['data'])
        stream.seek(0)
        stream.filename = filename
        self.image: Image.Image = Image.open(stream)
        del stream

        # todo
        row = Counter()

        self.grid_columnconfigure(1, weight=1)

        tk.Label(self, text=lang('File:')).grid(row=row(), column=0, sticky=W)
        self.filepath = tk.Entry(self, relief=FLAT)
        self.filepath.grid(row=row(), column=1, sticky=EW)
        basedir = os.path.join(os.environ['USERPROFILE'], 'Downloads')
        if not os.path.exists(basedir): basedir = os.environ['IDEA_INITIAL_DIRECTORY']
        defaultpath = os.path.join(basedir, filename)
        self.filepath.insert(END, defaultpath)
        self.filepath.configure(state='readonly')
        tk.Button(self, text='🗁', command=self.askfilepath).grid(row=row(), column=2)

        row.step()
        ImageStats(self, self.image, self.data).grid(row=row(), column=1, columnspan=2, sticky=EW)
        row.step()
        thumb = self.image.copy()
        thumb.thumbnail((300, 300))
        self.imgtk = ImageTk.PhotoImage(thumb)
        del thumb
        tk.Label(self, image=self.imgtk).grid(row=row(), column=1, sticky=NW)

        row.step()
        self.grid_rowconfigure(row(), weight=1)
        tk.Button(self, text=lang('Export'), command=self.export).grid(row=row(), column=1, columnspan=2, sticky=SE, padx=5, pady=5)

    def load(self) -> sql.Row:
        connection = sql.connect(DATABASEPATH)
        connection.row_factory = sql.Row
        connection.create_function('str', 1, str)
        try:
            QUERY = r'SELECT str(basename) as basename, extension, data FROM images WHERE rowid = ? LIMIT 1'

            cursor = connection.execute(QUERY, [self.rowid])

            return cursor.fetchone()
        finally:
            connection.close()

    def export(self):
        path = self.filepath.get()
        if not path or os.path.isdir(path): raise NotAFileError(lang('Invalid file entered'))

        # unused because file-input is handled via ask-save-as-filedialog
        # if os.path.isfile(path):
        #     if not messagebox.askokcancel(
        #         title=lang('Save as confirm'),
        #         message=lang('File allready exists. Do you want to continue?')
        #     ):
        #         return

        img = self.image

        if getattr(img, 'is_animated', False):
            print("Try to export as animated")
            try:
                imgs = [(img.seek(n), img.copy())[1] for n in range(1, img.n_frames)]
                img.seek(0)
                img.save(path, save_all=True, append_images=imgs)
                messagebox.showinfo(message=lang('File exported'))
            except Exception:
                messagebox.showwarning(message=lang('Failed to save animated. Continue with single image'))
            else:
                return

        print("Export as image")
        img.save(path)

        messagebox.showinfo(message=lang('File exported'))

    def askfilepath(self):
        oldpath = self.filepath.get()
        dirpath, filename = os.path.split(oldpath)
        oldext = os.path.splitext(filename)[1]
        filetypes = [(self.image.format_description, '*.{}'.format(self.image.format.lower()))]
        filetypes.extend(self.get_filetypes())
        pprint(filetypes)
        initialdir = dirpath
        initialfile = filename or self.filename

        filepath = filedialog.asksaveasfilename(
            defaultextension=oldext,
            filetypes=filetypes,
            initialdir=initialdir,
            initialfile=initialfile,
        )
        if not filepath: return
        self.filepath.configure(state='normal')
        self.filepath.delete(0, END)
        self.filepath.insert(END, filepath)
        self.filepath.configure(state='readonly')

    @staticmethod
    def get_filetypes() -> T.List[T.Tuple[str, str]]:
        back = []
        Image.preinit()  # not necessary but to be sure
        Image.init()  # not necessary but to be sure
        for value, _ in Image.OPEN.values():
            try:
                ext = '*.{}'.format(value.format.lower())
                desc = value.format_description
                back.append((desc, ext))
            except AttributeError:
                pass
        back.append((lang('All Files'), '*.*'))
        return back

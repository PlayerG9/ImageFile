r"""
- Limit
- Auto-Vacuum
- decompression_bomb_check
- message on not images
- duplicatewarning

todo
fast-import  # checks only filesname
image-import  # checks for file-content

☽ 🌚
☀ 🌝
"""
from imports import *


THEME = T.Dict[str, T.Dict[str, T.Dict[str, T.Any]]]
LIGHTMODE: THEME = json.load(open(os.path.join(MEMORYDIR, 'lightmode.json')))
DARKMODE: THEME = json.load(open(os.path.join(MEMORYDIR, 'darkmode.json')))


class MessageBox(tk.Message):
    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)
        self.bind('<Configure>', lambda e: self.__resize())

    def __resize(self):
        self.configure(width=self.winfo_width())


class NumberEntry(tk.Entry):
    def __init__(self, master, from_: int, to: int, **kwargs):
        super().__init__(master, **kwargs)
        self.from_ = from_
        self.to = to
        self.bind('<Key>', self.key)
        self.bind('<FocusOut>', self.leave_limit)

    def set(self, value: int):
        self.delete(0, END)
        self.insert(END, str(value))

    def get(self):
        return int(super().get())

    @staticmethod
    def key(event):
        char: str = event.char
        if not char: return
        if not char.isprintable(): return
        if not char.isdigit(): return 'break'

    def leave_limit(self, _):
        if int(self.get()) < self.from_:
            self.set(self.from_)
        elif self.get() > self.to:
            self.set(self.to)


class SettingsFrame(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # self.tabs = ttk.Notebook(self)
        # self.tabs.grid(row=0, column=0, sticky=NSEW)
        self.items = [
            ProgrammSettings(self),
            ImageSettings(self),
        ]
        for item in self.items:
            item.pack(fill=X)
            # self.tabs.add(item, text=item.text)

        # no frame with save button
        # frame = tk.Frame(self)
        # frame.grid(row=1, column=0, sticky=EW)

        self.bind('<Leave>', lambda e: self.save_changes())

    def save_changes(self):
        print('Save-Setting-Changes')
        self.focus_set()
        self.update()
        # for tab in self.tabs.tabs():
        #    if isinstance(tab, str):
        #        tab = self.nametowidget(tab)
        #
        #    if hasattr(tab, 'save_changes'):
        #        tab.save_changes()
        for item in self.items:
            if hasattr(item, 'save_changes'):
                item.save_changes()

        EventHandler.invoke('<Updated-Settings>')


class ProgrammSettings(tk.LabelFrame):
    def __init__(self, master):
        super().__init__(master, text=lang('Programm'))
        self.grid_columnconfigure(2, weight=1)

        row = Counter()

        tk.Label(self, text=lang("Displaylimit:")).grid(row=row(), column=0, sticky=NW)
        self.e_limit = NumberEntry(self, from_=10, to=500)
        self.e_limit.set(config('resultlimit'))
        self.e_limit.grid(row=row(), column=1, sticky=EW)
        msg = lang("The maxixum of listed results")
        MessageBox(self, text=msg, anchor=NE).grid(row=row(), column=2, sticky='new')

        row.step()
        tk.Label(self, text=lang("Autocleanup:")).grid(row=row(), column=0, sticky=NW)
        self.e_autovacuum = tk.BooleanVar(self, value=config('auto-vacuum'))
        tk.Checkbutton(self, variable=self.e_autovacuum, anchor=W).grid(row=row(), column=1, sticky=W)
        msg = lang("Automatically freeing of memory in the database")
        MessageBox(self, text=msg, anchor=NE).grid(row=row(), column=2, sticky='new')

        row.step()
        tk.Button(self, text=lang('Manuell cleanup'), command=self.vacuum).grid(row=row(), column=1, sticky=EW)

        # disabled dark/light-mode
        """row.step()
        frame = tk.Frame(self)
        frame.grid(row=row(), columnspan=3, sticky=EW, pady=10)
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_columnconfigure(1, weight=1)

        self.theme = None
        btnconf = dict(font=(None, 20), relief=GROOVE)
        self.style = ttk.Style()
        # self.tk.call('lappend', 'auto_path', os.path.join(MEMORYDIR, 'awthemes'))
        # self.tk.call('package', 'require', 'awdark')
        # self.style.theme_create('theme-awdark', 'awdark')
        # self.tk.call('package', 'require', 'awlight')
        # self.style.theme_create('theme-awlight', 'awlight')
        print(self.style.theme_names())
        self.style.theme_create(f'theme-light', 'alt')
        self.style.theme_create(f'theme-dark', 'alt')
        style = self.style
        for element, options in DARKMODE['style'].items():
            for key, value in options.get('configure', {}).items():
                style.configure(f'theme-dark.{element}', **{key: value})
        tk.Button(frame, **btnconf, text='☀', command=lambda: self.change_theme(LIGHTMODE, 'light')).grid(row=0, column=0, sticky=E, padx=10)
        tk.Button(frame, **btnconf, text='☽', command=lambda: self.change_theme(DARKMODE, 'dark')).grid(row=0, column=1, sticky=W, padx=10)
        if config('theme') == 'light': self.change_theme(LIGHTMODE, 'light')
        else: self.change_theme(DARKMODE, 'dark')  # default"""

    def save_changes(self):
        print(f'{self.e_limit.get()=}')
        config.set('resultlimit', self.e_limit.get())
        config.set('auto-vacuum', self.e_autovacuum.get())

    def vacuum(self):
        try:
            self.grab_set()
            tk._default_root.configure(cursor='wait')
            EventHandler.invoke('<Vacuum>')
            tk._default_root.configure(cursor='')
            messagebox.showinfo(message=lang('Memory freed'))
        finally:
            self.grab_release()

    """def change_theme(self, themedata, themename):
        if themename is self.theme: return
        self.theme = themename
        self.style.theme_use(f'theme-{themename}')

        for cls, options in themedata['configure'].items():
            root: tk.Tk = tk._default_root
            if not cls:
                self.apply(**options)
                for key, value in options.items():
                    root.option_add(f"*{key}", value)
            else:
                self.apply(test=lambda w: w.__class__.__name__ == cls, **options)
                for key, value in options.items():
                    root.option_add(f"*{cls}.{key}", value)

        # print("Print Elements:")
        # for elementname in style.element_names():
        #     print(elementname)
        #     pprint(style.element_options(elementname))

    def iter_all(self, master=None) -> T.Iterator[tk.Widget]:
        master: tk.Widget = master or tk._default_root
        for child in master.winfo_children():
            yield child
            yield from self.iter_all(child)
        # try: self.update()
        # except tk.TclError: pass

    def apply(self, test=lambda w: True, **kwargs):
        for key, value in kwargs.items():
            for widget in self.iter_all():
                if not test(widget): continue
                try:
                    widget.configure({key: value})
                except tk.TclError:
                    # traceback.print_exception(type(exc), exc, exc.__traceback__)  # spams the console
                    pass"""


class ImageSettings(tk.LabelFrame):
    r"""
- decompression_bomb_check
- message on not images
- duplicatewarning
    """
    def __init__(self, master):
        super().__init__(master, text=lang('Images'))
        self.grid_columnconfigure(2, weight=1)

        row = Counter()

        tk.Label(self, text=lang("Zip-Bomb Test")).grid(row=row(), column=0, sticky=W)
        self.e_bompcheck = tk.BooleanVar(self, value=config('zip-bomb test'))
        tk.Checkbutton(self, variable=self.e_bompcheck, anchor=W).grid(row=row(), column=1, sticky=W)
        msg = lang("Check if the imported file is a possible zip-bomp (> {} pixel)").format(Image.MAX_IMAGE_PIXELS)
        MessageBox(self, text=msg, anchor=NE).grid(row=row(), column=2, sticky='new')
        if config('zip-bomb test'): Image.MAX_IMAGE_PIXELS = ORIG_MAX_IMAGE_PIXELS
        else: Image.MAX_IMAGE_PIXELS = None

        row.step()
        tk.Label(self, text=lang("No-image message")).grid(row=row(), column=0, sticky=W)
        self.e_noimagewarning = tk.BooleanVar(self, value=config('no-image message'))
        tk.Checkbutton(self, variable=self.e_noimagewarning, anchor=W).grid(row=row(), column=1, sticky=W)
        msg = lang("gives a warning if a file in the imported folder is not an image")
        MessageBox(self, text=msg, anchor=NE).grid(row=row(), column=2, sticky='new')

        row.step()
        tk.Label(self, text=lang("Duplicate protection")).grid(row=row(), column=0, sticky=W)
        self.e_duplicate = tk.BooleanVar(self, value=config('duplicate protection'))
        tk.Checkbutton(self, variable=self.e_duplicate, anchor=W).grid(row=row(), column=1, sticky=W)
        msg = lang("Does not import duplicate images")
        MessageBox(self, text=msg, anchor=NE).grid(row=row(), column=2, sticky='new')

    def save_changes(self):
        bomb_check = self.e_bompcheck.get()
        config.set('zip-bomb test', bomb_check)
        if bomb_check: Image.MAX_IMAGE_PIXELS = ORIG_MAX_IMAGE_PIXELS
        else: Image.MAX_IMAGE_PIXELS = None
        config.set('no-image message', self.e_noimagewarning.get())
        config.set('duplicate protection', self.e_duplicate.get())

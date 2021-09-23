from imports import *
from .statsheader import StatsHeader


class SearchHeader(tk.Frame):
    def __init__(self, master):
        """
        Args:
            master:
        """
        super().__init__(master)
        self.grid_columnconfigure(1, weight=1)

        tk.Label(self, text=lang('Search:')).grid(row=0, column=0)

        self.entry = tk.Entry(self)
        self.entry.grid(row=0, column=1, sticky=EW)
        self.entry.bind('<Return>', lambda _: EventHandler.invoke('<Search>'))
        self.bind_all('<Control-f>', lambda e: self.entry.focus_set())
        options = [''] + self.get_extensions()
        EventHandler.register('<Updated-Files>', self.update_keys)
        self.extension = tk.StringVar(self)
        self.extension_w = ttk.OptionMenu(self, self.extension, options[0], *options, command=lambda _: EventHandler.invoke('<Search>'))
        self.extension_w.grid(row=0, column=2, sticky=NSEW)

        self.search_styles = {
            lang('Text'): 'txt',
            lang('Simple Expression'): 'se',
            lang('Regular Expression'): 're'
        }
        options = list(self.search_styles.keys())
        self.search_style = tk.StringVar(self)
        self.search_style_w = ttk.OptionMenu(self, self.search_style, options[1], *options, command=lambda _: EventHandler.invoke('<Search>'))  # only 'command' allowed here
        # self.search_style_w.configure(anchor=W)
        self.search_style_w.grid(row=1, columnspan=2, sticky=EW)

        self.order_by_list = {
            lang('Name'): 'basename',
            lang('Time'): 'timestamp',
            lang('Size'): 'filesize'
        }
        options = list(self.order_by_list.keys())
        self.order_by = tk.StringVar(self)
        self.order_by_w = ttk.OptionMenu(self, self.order_by, options[0], *options, command=lambda _: EventHandler.invoke('<Search>'))  # only 'command' allowed here
        # self.order_by_w.configure(anchor=W)
        self.order_by_w.grid(row=1, column=2, sticky=EW)

        # tags
        # self.tags_filter = tk.StringVar(self)
        self.tags_filter = TagFilter(self, command=lambda: EventHandler.invoke('<Search>'))
        self.tags_filter.grid(row=2, columnspan=3, sticky=EW)

        StatsHeader(self).grid(row=3, columnspan=3, sticky=EW, pady=2)

    def get_data(self) -> dict:
        return {
            'query': self.entry.get(),
            'ext': self.extension.get(),
            'style': self.search_styles[self.search_style.get()],
            'order': self.order_by_list[self.order_by.get()],
            'tags': self.tags_filter.get_tags()
        }

    def update_keys(self):
        options = [''] + self.get_extensions()
        last = self.extension.get()
        self.extension_w.set_menu(last if last in options else '', *options)
        # self.extension_w.destroy()
        # self.extension_w = tk.OptionMenu(self, self.extension, *options, command=lambda _: EventHandler.invoke('<Search>'))
        # self.extension_w.grid(row=0, column=2, sticky=NSEW)

    @staticmethod
    def get_extensions() -> T.List[str]:
        connection = sql.connect(DATABASEPATH)
        try:
            QUERY = r'SELECT DISTINCT LOWER(extension) FROM images'

            raw = connection.execute(QUERY).fetchall()
            return [e[0] for e in raw]
        finally:
            connection.close()

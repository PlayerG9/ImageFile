from imports import *
from searchframe import SearchFrame
from previewframe import PreviewFrame
from supports.filehandler import FileHandler
from frames import *


class Application(tkdnd.Tk):
    destroyed: bool

    def __init__(self):
        super().__init__()
        self.minsize(self.winfo_screenwidth() // 3, self.winfo_screenheight() // 3)
        self.geometry('{:.0f}x{:.0f}'.format(self.winfo_screenwidth() // 2, self.winfo_screenheight() // 2))
        self.title(os.path.basename(sys.executable))
        iconpath = os.path.join(MEMORYDIR, 'logo.ico')
        if os.path.isfile(iconpath):
            self.wm_iconbitmap(iconpath)

        self.load_config()

        self.init_menu()

        # FlyingDebugPopup()

        self.filehandler = FileHandler()

        self.pane = tk.PanedWindow(
            master=self,
            sashwidth=10,
            opaqueresize=False
        )
        self.pane.place(relwidth=1.0, relheight=1.0)
        self.searchframe = SearchFrame(self)
        self.previewframe = PreviewFrame(self)

        self.settingframe = SettingsFrame(self)
        self.statframe = StatisticsFrame(self)

        self.pane.add(self.searchframe, minsize=200, width=300)
        self.pane.add(self.previewframe)

    def run(self):
        self.mainloop()
        self.destroyed = True
        try: self.withdraw()
        except tk.TclError: pass
        if config('auto-vacuum'):
            warn('remove free space in the database')
            EventHandler.invoke('<Vacuum>')  # remove free space from the database

    def report_callback_exception(self, exc, val, tb):
        """
        Args:
            exc:
            val:
            tb:
        """
        if isinstance(val, SilentError): return
        traceback.print_exception(exc, val, tb)
        if getattr(self, 'destroyed', False): return
        messagebox.showerror(
            lang('Catched Error'),
            '\n'.join(traceback.format_exception(exc, val, tb))
        )

    def load_config(self):
        with open(os.path.join(MEMORYDIR, 'tkconf.json'), encoding='utf-8') as file:
            configdata: dict = json.load(file)

        for key, value in configdata.items():
            try:
                self.option_add(key, value)
            except tk.TclError as exc:
                self.report_callback_exception(type(exc), exc, exc.__traceback__)

    def init_menu(self):
        menu = tk.Menu(self, tearoff=0)

        menu.add_command(
            label=lang('Quit'),
            command=self.quit
        )
        settings = lang('Settings')
        menu.add_command(
            label=settings,
            command=lambda: EventHandler.invoke('<Show-Widget>', self.settingframe, text=settings)
        )
        stats = lang('Stats')
        menu.add_command(
            label=stats,
            command=lambda: EventHandler.invoke('<Show-Widget>', self.statframe, text=stats)
        )

        self.configure(menu=menu)


def main():
    app = Application()
    app.run()


if __name__ == '__main__':
    main()

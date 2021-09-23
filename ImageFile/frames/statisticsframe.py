from imports import *


class StatisticsFrame(tk.Frame):
    def __init__(self, master):
        """
        Args:
            master:
        """
        super().__init__(master)
        self.bind('<Expose>', lambda e: self.update_stats())
        EventHandler.register('<Updated-Files>', self.update_stats)

        row = Counter()

        tk.Label(self, text=lang('Databasesize:')).grid(row=row(), sticky=W)
        self.lbl_dbsize = tk.Label(self)
        self.lbl_dbsize.grid(row=row(), column=1, sticky=W)

        row.step()
        tk.Label(self, text=lang('Previewsize:')).grid(row=row(), sticky=W)
        self.lbl_previewsize = tk.Label(self)
        self.lbl_previewsize.grid(row=row(), column=1, sticky=W)

        row.step()
        tk.Label(self, text=lang('Total images:')).grid(row=row(), sticky=W)
        self.lbl_totalimages = tk.Label(self)
        self.lbl_totalimages.grid(row=row(), column=1, sticky=W)

        row.step()
        tk.Label(self, text=lang('Total tags:')).grid(row=row(), sticky=W)
        self.lbl_totaltags = tk.Label(self)
        self.lbl_totaltags.grid(row=row(), column=1, sticky=W)

    def update_stats(self):
        print("UPDATE STATS")
        if not self.winfo_viewable(): return  # hidden
        self.lbl_dbsize.configure(text=format_filesize(self.databasesize()))
        self.lbl_previewsize.configure(text=format_filesize(self.preview_sizes()))
        self.lbl_totalimages.configure(text=self.total_images())
        self.lbl_totaltags.configure(text=self.total_tags())

    @staticmethod
    def databasesize():
        return os.path.getsize(DATABASEPATH)

    @staticmethod
    def total_images():
        connection = sql.connect(DATABASEPATH)
        try:
            return connection.execute('SELECT COUNT(*) FROM images').fetchone()[0]
        finally:
            connection.close()

    @staticmethod
    def preview_sizes() -> int:
        connection = sql.connect(DATABASEPATH)
        try:
            return connection.execute("SELECT SUM(LENGTH(preview)) FROM images").fetchone()[0] or 0  # no images => None
        finally:
            connection.close()

    @staticmethod
    def total_tags():
        connection = sql.connect(DATABASEPATH)
        # noinspection PyTypeChecker
        connection.create_aggregate('collect', 1, TagCollectAggregate)
        try:
            raw = connection.execute('SELECT COLLECT(tags) FROM images').fetchone()[0]
            if not raw:
                return 0
            return len(raw.split('|'))
        finally:
            connection.close()

from imports import *


class StatsHeader(tk.Frame):
    def __init__(self, master):
        """
        Args:
            master:
        """
        super().__init__(master)
        self.grid_columnconfigure(0, weight=1)
        self.time = tk.Label(self, anchor=W)
        self.time.grid(row=0, column=0, sticky=EW)
        self.count = tk.Label(self, anchor=W)
        self.count.grid(row=0, column=1, sticky=EW)
        EventHandler.register('<Search-Stats>', self.on_search_stats)

    def on_search_stats(self, totaltime: float, count: int, found: int):
        """
        Args:
            totaltime (float):
            count (int):
            found (int):
        """
        self.time['text'] = lang('Time: {}s').format(totaltime)
        self.count['text'] = lang('{} of {}').format(count, found)

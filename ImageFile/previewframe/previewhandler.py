from imports import *
from .imagepreview import ImagePreview
from frames.exportframe import ExportFrame


class PreviewHandler(ttk.Notebook):
    def __init__(self, master):
        """
        Args:
            master:
        """
        super().__init__(master)
        self.opened: T.Dict[int, tk.Widget] = {}
        self.special = []

        self.bind('<Button-2>', self.on_scrollbutton)

        EventHandler.register('<Open>', self.on_open)
        EventHandler.register('<Delete-Files>', self.update_opened)
        EventHandler.register('<Show-Widget>', self.add_widget)
        EventHandler.register('<Export-Dialog>', self.export_dialog)

    def add_widget(self, widget, **kwargs):
        """
        Args:
            widget:
            **kwargs:
        """
        if widget not in self.special:
            self.add(widget, **kwargs)
            self.special.append(widget)
        self.select(widget)

    def on_open(self, rowid):
        """
        Args:
            rowid:
        """
        if rowid in self.opened:
            self.select(self.opened[rowid])
            return
        if len(self.opened) > 20:  # limit of 20
            k = tuple(self.opened.keys())[0]
            w = self.opened[k]
            del self.opened[k]
            w.destroy()
        w = ImagePreview(self, rowid)
        self.add(w, text=w.text, sticky=NSEW)
        self.select(w)
        self.opened[rowid] = w  # add after successfully loading

    def export_dialog(self, files: T.List[int]):
        for file in files:
            ExportFrame(file)
            # self.add_widget(w, text=)

    def update_opened(self, files: T.List[int]):
        """
        Args:
            files:
        """
        for rowid in files:
            if rowid in self.opened:
                self.opened[rowid].destroy()
                del self.opened[rowid]

    def on_scrollbutton(self, event):
        """
        Args:
            event:
        """
        if not self.identify(event.x, event.y): return
        tabindex = self.index('@{},{}'.format(event.x, event.y))
        name = self.tabs()[tabindex]
        w = self.nametowidget(name)
        if w in self.special:
            if getattr(w, 'alwaysdestroy', False):
                w.destroy()
            else:
                self.forget(w)
            self.special.remove(w)
        else:
            del self.opened[w.rowid]
            w.destroy()

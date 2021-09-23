import tkinter as tk
from tkinter.constants import *
from tkinter import ttk
import re
import sqlite3 as sql
import traceback
import io
import typing as T

from imports import warn
from PIL import Image
from CONSTANTS import DATABASEPATH


########################################################################################################################


def txt2re(txt: str) -> str:
    """
    Args:
        txt (str):
    """
    return re.escape(txt)


def se2re(se: str) -> str:
    """
    Args:
        se (str):
    """
    escaped = re.escape(se)
    return re.sub(r'\\\*|%', r'.*', escaped)


def sqlite3regexp(y, x) -> bool:
    """
    Args:
        y:
        x:
    """
    try:
        return bool(re.search(y, str(x), flags=re.IGNORECASE))
    except Exception as exc:
        print([y, x])
        warn('sqlite3regexp() raised an exception')
        traceback.print_exception(type(exc), exc, exc.__traceback__)
        raise exc


########################################################################################################################


def format_filesize(fsize: int) -> str:
    """
    Args:
        fsize (int):
    """
    if not isinstance(fsize, int): return str(fsize)
    if fsize > 1048576:
        return '{:.2f} MB'.format(fsize / 1048576)
    elif fsize > 1024:
        return '{:.2f} KB'.format(fsize / 1024)
    else:
        return'{:.0f} B'.format(fsize)


########################################################################################################################


def get_imagebytes(image: Image.Image, fileformat='PNG') -> bytes:
    """
    Args:
        image (Image.Image):
        fileformat:
    """
    fileformat = fileformat.removeprefix('.').upper()  # convert fileextension like '.png'
    stream = io.BytesIO()  # create stream
    image.save(stream, fileformat, optimize=True)  # save to stream
    stream.seek(0)  # go to point 0
    return stream.read()  # read everything


########################################################################################################################


class AutoScrollbar(tk.Scrollbar):
    def set(self, first, last):
        """
        Args:
            first:
            last:
        """
        if first == '0.0' and last == '1.0':
            self.grid_remove()
        else:
            self.grid()
        super().set(first, last)


class FlyingDebugPopup(tk.Menu):
    def __init__(self):
        super().__init__()

        self.add_command(label="Press to tearoff and continue")

        self.bind_all('<Motion>', self.update_text)

        self.post(0, 0)

    def update_text(self, event):
        """
        Args:
            event:
        """
        try:
            widget = event.widget
            if isinstance(widget, str):
                widget = self.nametowidget(widget)
            text = ttk.Widget.identify(widget, event.x, event.y)
            # event.widget.identify(event.x, event.y)
        except (tk.TclError, KeyError):
            text = "None"
        # print(["YEG", self.entryconfigure(1)])
        self.entryconfigure(1, label=text)


class BlockingProgressBar(ttk.Progressbar):
    def __init__(self, maximum: int = None):
        """
        Args:
            maximum (int):
        """
        super().__init__(mode='determinate' if maximum else 'indeterminate', maximum=maximum)
        self.automatic = not bool(maximum)

    def __enter__(self):
        self.grab_set()
        self.place(relx=0.35, rely=0.5, relwidth=0.3)
        if self.automatic:
            self.auto_update()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Args:
            exc_type:
            exc_val:
            exc_tb:
        """
        self.destroy()

    def auto_update(self):
        self['value'] = self['value'] + 1
        self.after(10, self.auto_update)

    def set(self, value):
        """
        Args:
            value:
        """
        self['value'] = value

    def step(self):
        self['value'] = self['value'] + 1


class TagEntry(tk.Frame):
    get_tags: callable

    def __init__(self, master=None, **kwargs):
        tags = kwargs.pop('tags', ())
        kwargs.update(relief=RIDGE, borderwidth=2)
        super().__init__(master, **kwargs)
        self.grid_columnconfigure(1000, weight=1)
        self.bind('<Button-1>', lambda e: self.entry.focus_set())

        for tag in tags:
            TagWidget(self, text=tag)

        self.entry = tk.Entry(self, relief=FLAT)
        self.entry.grid(row=0, column=1000, sticky=NSEW)
        self.entry.bind('<Key>', self.on_key)
        self.entry.bind('<Return>', lambda e: self.add_tag())
        self.entry.bind('<FocusOut>', self.on_leave)

        self.rearrange()

    def destroy(self):
        tags = self.get_tags()
        self.get_tags = lambda: tags
        super().destroy()

    def get_tags(self) -> T.Tuple[str]:
        back = []
        for child in self.winfo_children():
            if child is self.entry: continue
            back.append(child.get_tag())
        return back

    def add_tag(self):
        tag = self.entry.get()
        if not tag: return
        self.entry.delete(0, END)
        TagWidget(self, text=tag)
        self.rearrange()

    def rearrange(self):
        for i, w in enumerate(self.winfo_children()):
            if w is self.entry: continue
            w.grid(row=0, column=i, padx=1, pady=2)

    def on_key(self, event):
        # print(event)
        char: str = event.char
        if not char.isprintable(): return
        if not char.isascii(): return 'break'
        if char == '|':
            self.add_tag()
            return 'break'

    def on_leave(self, _):
        self.entry.delete(0, END)


class TagFilter(tk.Frame):
    get_tags: callable

    def __init__(self, master, **kwargs):
        self.command = kwargs.pop('command', lambda: None)
        kwargs.update(borderwidth=2, relief=GROOVE, background='white', height=25)
        super().__init__(master, **kwargs)
        # self.grid_columnconfigure(1000, weight=1)
        self.menu = tk.Menu(self, tearoff=0)
        self.menu.add_command(label="-----")
        self.bind('<Button>', lambda e: self.invoke())

    def destroy(self):
        tags = self.get_tags()
        self.get_tags = lambda: tags
        super().destroy()

    def invoke(self):
        self.update_tags()
        x = self.winfo_rootx()
        y = self.winfo_rooty() + self.winfo_height()
        self.menu.post(x, y)

    def get_tags(self) -> T.List[str]:
        back = []
        for child in self.winfo_children():
            if child is self.menu: continue
            back.append(child.get_tag())
        return back

    def add_tag(self, tag):
        if not tag: return
        t = TagWidget(self, text=tag)
        t.lbl.bind('<Button>', lambda e: self.invoke())
        t.bind('<Destroy>', lambda e: self.after(10, self.command))  # use .after to ensure that the tag is removed
        self.rearrange()
        self.command()

    def rearrange(self):
        for i, w in enumerate(self.winfo_children()):
            if w is self.menu: continue
            w.grid(row=0, column=i, padx=1, pady=2)

    def update_tags(self):
        connection = sql.connect(DATABASEPATH, detect_types=True)
        connection.create_aggregate('collect', 1, TagCollectAggregate)
        try:
            QUERY = r'SELECT COLLECT(tags) FROM images'

            raw = connection.execute(QUERY).fetchone()
            if raw is None or raw[0] is None: return  # no rows in the database
            tags: T.List[str] = raw[0].split('|')

            print(tags)
            self.menu.delete(0, END)
            for tag in tags:
                self.menu.add_command(label=tag, command=lambda t=tag: self.add_tag(t))
        finally:
            connection.close()


class TagWidget(tk.Frame):
    def __init__(self, master=None, **kwargs):
        text = kwargs.pop('text')
        kwargs.update(
            relief=GROOVE,
            borderwidth=2
        )
        super().__init__(master, **kwargs)
        self.grid_columnconfigure(0, weight=1)

        self.lbl = tk.Label(self, text=text)
        self.lbl.grid(row=0, column=0, sticky=EW)
        b = tk.Label(self, text='✗', cursor='hand2')  # no button, because label are smaller
        b.bind('<ButtonRelease-1>', lambda e: self.destroy())
        # b.bind('<Enter>', lambda e: b.configure(relief=RAISED))
        # b.bind('<Leave>', lambda e: b.configure(relief=FLAT))
        b.grid(row=0, column=1, sticky=NSEW)

    def configure(self, **kw):
        if 'text' in kw:
            self.lbl.configure(text=kw.pop('text'))
        if not kw: return
        super().configure(**kw)

    def get_tag(self) -> str:
        return self.lbl['text']


########################################################################################################################


class Counter:
    def __init__(self):
        self.i = 0

    def step(self):
        self.i += 1

    def __call__(self):
        return self.i


class TagCollectAggregate:
    def __init__(self):
        self.tags = set()

    def step(self, value: str):
        for element in value.split(b'|'):
            self.tags.add(element)

    def finalize(self):
        return (b'|'.join(sorted(self.tags))).decode('ascii')

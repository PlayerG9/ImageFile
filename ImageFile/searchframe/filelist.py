from imports import *


class FileList(ttk.Treeview):
    # noinspection PyUnresolvedReferences
    def __init__(self, master=None, **kwargs):
        style = ttk.Style(master)
        style.configure('mystyle.Treeview', )  # , font=(None, 12))
        style.configure("mystyle.Treeview.Heading", font=(None, 11, 'bold'))  # , font=('Segoe UI', 12))
        super().__init__(master, columns=['ext'], style='mystyle.Treeview', **kwargs)
        self.heading('#0', text=lang('File'))
        self.column('#0', minwidth=150, width=200, stretch=YES)
        self.heading('ext', text=lang('Type'))
        self.column('ext', minwidth=40, width=40, stretch=NO)

        # self.event_b1 = None
        # self.bind('<Button-1>', self.event_button_1)
        # self.bind('<ButtonRelease-1>', self.event_buttonrelease_1)
        self.bind('<Button-3>', self.event_button_3)

        self.bind('<Double-Button>', lambda _: self.open_files())
        self.bind('<Return>', lambda _: self.open_files())

        self.bind('<Control-a>', lambda e: self.selection_set(self.get_children('')))
        # self.bind('<Control-v>', lambda e: self.paste_from_clipboard())  # currently not implemented
        self.bind('<Delete>', lambda e: self.delete_selection())

        self.is_dragging = False
        self.images: T.Set[tk.PhotoImage] = set()

        self.drop_target_register(tkdnd.DND_FILES)
        self.dnd_bind('<<DropEnter>>', self.drop_enter)
        self.dnd_bind('<<DropPosition>>', self.drop_position)
        self.dnd_bind('<<DropLeave>>', self.drop_leave)
        self.dnd_bind('<<Drop>>', self.drop)

        self.drag_source_register(1, tkdnd.DND_FILES)
        self.dnd_bind('<<DragInitCmd>>', self.drag_init)
        self.dnd_bind('<<DragEndCmd>>', self.drag_end)

    def set(self, data: T.List[sql.Row], reset_selection=False):
        selection = () if reset_selection else self.selection()
        self.delete(*self.get_children(''))
        for img in self.images:
            img.__del__()
        self.images.clear()
        for row in data:
            image: Image.Image = Image.open(BytesIO(row['preview']), formats=['PNG'])
            imagetk = ImageTk.PhotoImage(image)
            self.images.add(imagetk)
            self.insert('', END, row['rowid'], text=row['basename'], values=[row['extension']], image=imagetk)
        for sel in selection:
            try: self.selection_add(sel)
            except tk.TclError: pass  # removed item

    def open_files(self):
        for rowid in self.selection():
            EventHandler.invoke('<Open>', rowid)

    # def event_button_1(self, event):
    #     """self.event_b1 = event
    #     index = self.identify_row(event.y)
    #     if not index: return
    #     selection = self.selection()
    #     if not selection: return
    #     pprint([index, selection])
    #     if len(selection) == 1 and index == selection[0]: return  # to enable double-click
    #     if index in selection:  # prevent new selection, if over current selection
    #         return 'break'"""
    #
    # def event_buttonrelease_1(self, event):
    #     """event2 = self.event_b1
    #     index = self.identify_row(event.y)
    #     if not index: return
    #     if event.x == event2.x and event.y == event2.y:
    #         if index in self.selection():
    #             self.selection_set(index)"""

    def event_button_3(self, event):
        index = self.identify_row(event.y)
        if not index: return
        if index not in self.selection():
            self.selection_set(index)

        menu = tk.Menu(self, tearoff=0)

        # menu.add_command(label=lang("Rename"))  # todo
        # menu.add_separator()
        menu.add_command(label=lang("Export"), command=lambda: EventHandler.invoke('<Export-Dialog>', self.selection()))
        menu.add_separator()
        menu.add_command(label=lang("Delete"), foreground='red', command=self.delete_selection)

        menu.post(event.x_root, event.y_root)

    # currently not implemented
    """def paste_from_clipboard(self):
        try:
            ImageGrab.grabclipboard()
        except NotImplementedError:
            pass  # not supported on the os"""

    def delete_selection(self):
        if not messagebox.askyesno(lang("Delete?"), lang('Are you sure you want to delete these images?')):
            return
        EventHandler.invoke('<Delete-Files>', self.selection())
        EventHandler.invoke('<Updated-Files>')

    def drop_enter(self, event):
        event.widget.focus_force()
        print(f'enter: {event.__dict__=}')
        files = self.tk.splitlist(event.data)
        print(f'{files=}')
        return tkdnd.COPY  # tkdnd.COPY

    def drop_position(self, event):
        # print(f'position: {event.__dict__=}')
        return event.action

    def drop_leave(self, event):
        print(f'leave: {event.__dict__=}')
        return event.action

    def drop(self, event):
        if self.is_dragging:
            # the canvas itself is the drag source
            return tkdnd.REFUSE_DROP
        print(f'drop: {event.__dict__=}')
        if event.data:
            files = self.tk.splitlist(event.data)
            print(f'{files=}')
            self.after(10, lambda f=files: self._drop(f))
        return event.action

    def _drop(self, files):
        for file in files:
            try:
                if os.path.isdir(file):
                    EventHandler.invoke('<Import-Directory>', file)
                else:
                    EventHandler.invoke('<Import-File>', file)
            except (NotAFileError, NotADirectoryError) as exc:
                tk._default_root.report_callback_exception(type(exc), exc, exc.__traceback__)
            try: self.update()  # keep window alive
            except tk.TclError: pass
        EventHandler.invoke('<Updated-Files>')

    def drag_init(self, event):
        self.is_dragging = True
        print(f'init: {event.__dict__=}')
        selection = self.selection()
        if not selection: return 'break'
        tempfiles = []
        EventHandler.invoke('<Export-Prepare>', selection, tempfiles)
        # data = file
        return (tkdnd.ASK, tkdnd.COPY), tkdnd.DND_FILES, tempfiles

    def drag_end(self, _):
        self.is_dragging = False
        EventHandler.invoke('<Export-Cleanup>')

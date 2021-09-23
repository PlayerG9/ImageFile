from imports import *
from .searchheader import SearchHeader
from .filelist import FileList


class SearchFrame(tk.LabelFrame):
    def __init__(self, master):
        super().__init__(
            master=master,
            text=lang("Search")
        )
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.search_header = SearchHeader(self)
        self.search_header.grid(row=0, column=0, columnspan=2, sticky=EW)

        self.list = FileList(self)
        self.list.grid(row=1, column=0, sticky=NSEW)
        yscroll = AutoScrollbar(self, orient=VERTICAL, command=self.list.yview)
        yscroll.grid(row=1, column=1, sticky=NS)
        self.list.configure(yscrollcommand=yscroll.set)

        EventHandler.register('<Search>', self.search)
        EventHandler.register('<Updated-Files>', self.search)
        EventHandler.register('<Updated-Settings>', self.search)
        self.after(50, self.search)

    def search(self):
        data = self.search_header.get_data()
        if data['style'] == 'txt':
            regex = txt2re(data['query'])
        elif data['style'] == 'se':
            regex = se2re(data['query'])
        else:
            regex = data['query']

        extension = data['ext']
        order = data['order']
        tags = data['tags']

        print(f'{regex=}')
        print(f'{extension=}')
        print(f'{order=}')

        starttime = time.time()
        connection = sql.connect(DATABASEPATH, detect_types=True)
        connection.row_factory = sql.Row
        connection.create_function('regexp', 2, sqlite3regexp)
        try:
            args = []
            QUERY = r'SELECT rowid, basename, extension, preview FROM images'
            WHERE = []
            if regex:
                WHERE.append('basename REGEXP ?')
                args.append(regex)
            if extension:
                WHERE.append('LOWER(extension) = ?')
                args.append(extension)
            if tags:
                for tag in tags:
                    WHERE.append("tags LIKE '%{}%'".format(tag))
                    # args.append(tag)
            WHERE = (' WHERE ' + ' AND '.join(WHERE)) if WHERE else ''

            if order == 'basename':
                SORT = ' ORDER BY LOWER(basename)'
            elif order == 'timestamp':
                SORT = ' ORDER BY timestamp DESC'
            elif order == 'filesize':
                SORT = ' ORDER BY LENGTH(data) DESC'
            else:
                warn('no order by')
                SORT = ''

            QUERY += WHERE + SORT + f" LIMIT {config('resultlimit') or 200}"

            print(f'{WHERE=}')
            print(f'{QUERY=}')
            print(f'{args=}')
            found: int = connection.execute(r'SELECT COUNT(*) FROM images' + WHERE, args).fetchone()[0]

            cursor = connection.execute(QUERY, args)

            data = cursor.fetchall()
            self.list.set(data)
        finally:
            connection.close()
        totaltime = time.time() - starttime

        EventHandler.invoke('<Search-Stats>', totaltime=totaltime, found=found, count=len(data))

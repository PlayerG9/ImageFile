from imports import *


class FileHandler:
    def __init__(self):
        self.ensure_database()
        EventHandler.register('<Vacuum>', self.vacuum)
        EventHandler.register('<Delete-Files>', self.delete_files)
        EventHandler.register('<Import-File>', self.import_file)
        EventHandler.register('<Import-Directory>', self.import_directory)
        EventHandler.register('<Export-Prepare>', self.export_prepare)
        EventHandler.register('<Export-Cleanup>', self.export_cleanup)
        self.tempdirectory: tempfile.TemporaryDirectory = None

    @staticmethod
    def ensure_database():
        connection = sql.connect(DATABASEPATH)
        try:
            QUERY = r"SELECT name FROM sqlite_master WHERE type='table' AND name='images'"
            if not connection.execute(QUERY).fetchone():
                warn(f'invalid database. creating new')
                with open(os.path.join(MEMORYDIR, 'new_database.sql'), 'r', encoding='utf-8') as sqlfile:
                    connection.executescript(sqlfile.read())
        finally:
            connection.close()

    @staticmethod
    def vacuum():
        connection = sql.connect(DATABASEPATH)
        connection.set_progress_handler(tk._default_root.update, 100)
        try:
            connection.execute('VACUUM')
            connection.commit()
        finally:
            connection.close()

    @staticmethod
    def delete_files(files: T.List[int]):
        connection = sql.connect(DATABASEPATH)
        try:
            QUERY = r'DELETE FROM images WHERE rowid IN ({})'.format(','.join('?' * len(files)))

            connection.execute(QUERY, files)
            connection.commit()
        finally:
            connection.close()

    @staticmethod
    def import_file(path: str):
        if not os.path.isfile(path):
            raise NotAFileError(path)
        filename = os.path.split(path)[1]
        basename, extension = os.path.splitext(filename)

        dirpath = os.path.dirname(path)
        default_tag = [os.path.split(dirpath)[1]]

        image: Image.Image = Image.open(path)  # open image to check if acceptable and also for preview

        with open(path, 'rb') as imagefile:
            binary = imagefile.read()

        connection = sql.connect(DATABASEPATH)
        try:
            if config('duplicate protection') and connection.execute('SELECT 1 FROM images WHERE data = ? LIMIT 1', [binary]).fetchone():
                raise DuplicateImageError(f'{basename!r} allready exists in the database')

            # resize just now to prevent unnecessary computation
            image.thumbnail([16, 16])  # resize but keep aspect of the image (16 is the max width or height)
            # 2.62 KB
            preview = get_imagebytes(image)
            del image  # free mem
            print(f'{len(preview)=}')

            QUERY = 'INSERT INTO images (basename, extension, tags, preview, data) VALUES (?, ?, ?, ?, ?)'
            connection.execute(QUERY, (basename, extension, default_tag, preview, binary))
            connection.commit()
        finally:
            connection.close()

    @staticmethod
    def import_directory(path: str):
        if not os.path.isdir(path):
            raise NotADirectoryError(path)
        filecount = sum(len(f) for _, _, f in os.walk(path, followlinks=False))
        print(f'found {filecount=} files')
        with BlockingProgressBar(filecount) as progress:  # max_workers=1
            for root, dirs, files in os.walk(path, followlinks=False):
                for filename in files:
                    filepath = os.path.join(root, filename)
                    # print(f"{filepath=}")
                    try:
                        FileHandler.import_file(filepath)
                    except UnidentifiedImageError as exc:
                        if config('no-image message'):
                            tk._default_root.report_callback_exception(type(exc), exc, exc.__traceback__)
                    except Image.DecompressionBombError as exc:
                        tk._default_root.report_callback_exception(type(exc), exc, exc.__traceback__)
                    except DuplicateImageError:
                        pass
                    progress.step()
                    try: tk._default_root.update()
                    except tk.TclError: pass

    r"""  # unused because ThreadPoolExecutor and ProcessPoolexecutor are blocking at some point with a large sum of files
    @staticmethod
    def import_directory(path: str):
        if not os.path.isdir(path):
            raise NotADirectoryError(path)
        filecount = sum(len(f) for _, _, f in os.walk(path, followlinks=False))
        print(f'found {filecount=} files')
        with BlockingProgressBar(filecount) as progress, \
                ThreadPoolExecutor(max_workers=os.cpu_count() or 1) as pool:  # max_workers=1
            max_worker = pool._max_workers
            tasks = set()
            alltasks = set()
            for root, dirs, files in os.walk(path, followlinks=False):
                for filename in files:
                    filepath = os.path.join(root, filename)
                    # print(f"{filepath=}")
                    future = pool.submit(FileHandler.import_file, filepath)
                    future.add_done_callback(lambda f: (tasks.remove(f), progress.step()))
                    tasks.add(future)
                    alltasks.add(future)

                    while len(tasks) > max_worker:
                        try: tk._default_root.update()  # keep window alive
                        except tk.TclError: pass

            for task in alltasks:
                exc = task.exception()  # complete task
                if exc is not None:
                    try:
                        raise exc
                    except UnidentifiedImageError as exc:
                        if config('no-image message'):
                            tk._default_root.report_callback_exception(type(exc), exc, exc.__traceback__)
                    except Image.DecompressionBombError as exc:
                        tk._default_root.report_callback_exception(type(exc), exc, exc.__traceback__)
                    except DuplicateImageError:
                        pass
    """

    def export_prepare(self, rowids: T.List[int], tempfiles: list):
        warn('prepare export of files')
        self.tempdirectory = tempdirectory = tempfile.TemporaryDirectory()
        tmpdir = tempdirectory.name
        for rowid in rowids:
            data = self.load_filedata(rowid)
            filepath = self.get_filepath(tmpdir, data)
            with open(filepath, 'wb') as file:
                file.write(data['data'])
            tempfiles.append(filepath)
            del data

    def export_cleanup(self):
        warn('cleanup the created files')
        self.tempdirectory.cleanup()

    @staticmethod
    def load_filedata(rowid: int):
        connection = sql.connect(DATABASEPATH)
        connection.row_factory = sql.Row
        try:
            QUERY = r'SELECT * FROM images WHERE rowid = ? LIMIT 1'

            return connection.execute(QUERY, [rowid]).fetchone()
        finally:
            connection.close()

    @staticmethod
    def get_filepath(directory: str, data: sql.Row) -> str:
        basename = data['basename']
        extension = data['extension']
        filename = basename + extension
        counter = 1
        while os.path.exists(os.path.join(directory, filename)):
            filename = f'{basename} ({counter}){extension}'
            counter += 1
        return os.path.join(directory, filename)

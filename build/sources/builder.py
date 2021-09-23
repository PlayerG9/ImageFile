import os
import sys
from pprint import pprint
from os.path import abspath, join, dirname, basename

print("CWD:", os.getcwd())
import subprocess

APPNAME = "ImageFile"

BUILD = abspath(r'.\build')
CODE = abspath(r'.\ImageFile')
SOURCES = join(BUILD, 'sources')
TARGET = join(BUILD, APPNAME)

CMD = [
    abspath(r'.\venv\Scripts\pyinstaller.exe'),
    '--noconfirm',
    '--clean',
    '--distpath', BUILD,
    '--workpath', join(BUILD, 'build'),
    '--specpath', join(BUILD, 'build'),

    '--runtime-hook', join(SOURCES, r'.\hooker.py'),
    '--additional-hooks-dir', SOURCES,
    # '--version-file', os.path.abspath('./temp/build/version-file.py'),
    '--icon', join(SOURCES, 'logo.ico'),
    '--windowed',
    # '--hidden-import', '',
    '--add-data', f'{join(CODE, "memory")};memory',
    '--add-data', f'{join(CODE, "languages")};languages',

    '--name', APPNAME,
    join(CODE, '__main__.py')
]
pprint(CMD)

p = subprocess.run(CMD)
if p.returncode != 0:
    sys.exit(p.returncode)


WD = os.path.abspath(TARGET)
os.chdir(WD)
print("CWD:", os.getcwd())
LIBDIR = 'lib'
DLLDIR = 'windll'
os.mkdir(LIBDIR)
os.mkdir(DLLDIR)

for filename in os.listdir('./'):
    if os.path.isdir(filename): continue
    filext = os.path.splitext(filename)[1]
    if filext == '.pyd':
        os.replace(filename, os.path.join(LIBDIR, filename))
    if filext == '.dll':
        if filename.startswith('py'): continue
        os.replace(filename, os.path.join(DLLDIR, filename))


import sqlite3 as sql

conn = sql.connect('./memory/database.sl3')
conn.execute('DELETE FROM images')
conn.commit()
conn.execute('VACUUM')
conn.commit()
conn.close()

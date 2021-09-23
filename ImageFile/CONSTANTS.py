import sys as __sys
import os as __os


if getattr(__sys, 'frozen', None):
    APPDIR = __os.path.dirname(__sys.executable)
    DEBUG = False
else:
    APPDIR = __os.path.dirname(__file__)
    DEBUG = True

MEMORYDIR = __os.path.join(APPDIR, 'memory')
DATABASEPATH = __os.path.join(MEMORYDIR, 'database.sl3')

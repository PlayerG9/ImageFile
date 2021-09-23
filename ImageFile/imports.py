class SilentError(Exception): pass
class NotAFileError(OSError): pass
# class NotADirectoryError(OSError): pass  # already builtin
class DuplicateImageError(FileExistsError): pass


import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkinter import filedialog
from tkinter.constants import *

import os
import sys

import typing as T

import traceback
import warnings
from pprint import pprint, pformat
import time


def warn(message: str):
    """
    Args:
        message (str):
    """
    warnings.warn(message, RuntimeWarning, 999)


import sqlite3 as sql
import json

sql.register_converter('TAGS', lambda dbobj: str(dbobj, encoding='ascii').split('|'))  # convert database to object
sql.register_adapter(list, lambda pyobj: ('|'.join(str(e) for e in pyobj)).encode('ascii'))  # convert object to database

import re

import atexit

import tempfile

import locale
locale.setlocale(locale.LC_ALL, '')

import tkinterdnd2 as tkdnd

from PIL import Image, ImageTk, ImageGrab
import PIL.ImageGrab
from PIL import UnidentifiedImageError
ORIG_MAX_IMAGE_PIXELS = Image.MAX_IMAGE_PIXELS
from io import BytesIO

from CONSTANTS import *

from scripts import *

from eventhandler import EventHandler

from supports.configsupport import config

from supports.languagesupport import get_language as __get_language
lang = __get_language()
del __get_language


pprint({k: v for k, v in os.environ.items()})

# Image.preinit()
# Image.init()
# pprint({k: getattr(Image, k) for k in dir(Image)})
# # pprint(Image.OPEN)
# raise

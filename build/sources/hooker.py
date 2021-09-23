import os
from os.path import join, abspath, basename, dirname
import sys

APPDIR = dirname(sys.executable)
sys.path.append(join(APPDIR, 'lib'))
os.add_dll_directory(join(APPDIR, 'windll'))

import sys
import inspect
import os.path

filename = inspect.stack()[0].filename
dirpath = os.path.dirname(filename)
sys.path.append(os.path.join(dirpath, "core"))

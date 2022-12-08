import inspect
from pathlib import Path

def file_rel_path(relpath):
	filename = inspect.stack()[1].filename
	dirpath = Path(filename).parent.resolve()
	return dirpath.joinpath(relpath)

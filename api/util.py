import inspect
from pathlib import Path

def file_rel_path(relpath: str):
	filename = inspect.stack()[1].filename
	dirpath = Path(filename).resolve().parent
	return dirpath.joinpath(relpath).resolve()

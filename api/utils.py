import os
import shutil
import inspect
from pathlib import Path

def mkdirp(path: str | Path, recreate=False) -> None:
	if recreate:
		shutil.rmtree(path)
	os.makedirs(path, exist_ok=True)

def resolve_path(path: str | Path) -> Path:
	return Path(path).resolve()

def file_rel_path(relpath: str) -> Path:
	filename = inspect.stack()[1].filename
	dirpath = Path(filename).resolve().parent
	return dirpath.joinpath(relpath).resolve()

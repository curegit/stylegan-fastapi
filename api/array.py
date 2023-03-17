import base64
import numpy as np
from io import BytesIO
from numpy import ndarray
from api.types import Base64

def to_npy_base64(array: ndarray) -> Base64:
	io = BytesIO()
	np.save(io, array, allow_pickle=False)
	seq = io.getvalue()
	string = base64.b64encode(seq).decode("ascii")
	return string

def from_npy_base64(npy: Base64) -> ndarray:
	bs = base64.b64decode(npy)
	obj = np.load(bs, allow_pickle=False)
	match obj:
		case ndarray() as array:
			return array
	raise RuntimeError()

def validate_array(array: ndarray, shape: tuple[int] | tuple[()] | None = None, dtype: str | type | None = None) -> bool:
	if shape is not None:
		if array.shape != shape:
			return False
	if dtype is not None:
		if array.dtype != dtype:
			return False
	return True

def clamp_array(array: ndarray, min: int | float | None, max: int | float | None, replace_nan: bool | int | float = True):
	match replace_nan:
		case False:
			x = array
		case True:
			x = np.nan_to_num(array, posinf=np.inf, neginf=-np.inf)
		case int() | float() as val:
			x = np.nan_to_num(array, nan=val, posinf=np.inf, neginf=-np.inf)
	return np.clip(x, min, max)

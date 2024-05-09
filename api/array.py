import base64
import numpy as np
from io import BytesIO
from numpy import ndarray
from api.types import Base64

def to_npy_base64(array: ndarray) -> Base64:
	io = BytesIO()
	np.save(io, array, allow_pickle=False)
	buf = io.getbuffer()
	string = base64.b64encode(buf).decode("ascii")
	return string

def from_npy_base64(npy: Base64) -> ndarray:
	bs = base64.b64decode(npy)
	with BytesIO(bs) as io:
		obj = np.load(io, allow_pickle=False)
		match obj:
			case ndarray() as array:
				return array
		raise ValueError()

def validate_array(array: ndarray, shape: tuple[int, ...] | tuple[()] | None = None, dtype: str | type | None = None) -> bool:
	if shape is not None:
		if array.shape != shape:
			return False
	if dtype is not None:
		if array.dtype != dtype:
			return False
	return True

def clamp_array(array: ndarray, min: int | float | None, max: int | float | None, replace_nan: bool | int | float = True) -> ndarray:
	match replace_nan:
		case False:
			x = array
		case True:
			x = np.nan_to_num(array, posinf=np.inf, neginf=-np.inf)
		case int() | float() as val:
			x = np.nan_to_num(array, nan=val, posinf=np.inf, neginf=-np.inf)
	return np.clip(x, min, max)

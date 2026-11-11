import base64
import numpy as np
from io import BytesIO
from math import prod
from numpy import ndarray
from api.types import Base64

# Very relaxed limits
# A normal 512-dimensional float32 vector takes only about 2 KiB
MAX_NPY_BYTES = 1024 * 1024
MAX_NPY_BASE64_LENGTH = 4 * ((MAX_NPY_BYTES + 2) // 3)

def to_npy_base64(array: ndarray) -> Base64:
	io = BytesIO()
	np.save(io, array, allow_pickle=False)
	buf = io.getbuffer()
	string = base64.b64encode(buf).decode("ascii")
	return string

def from_npy_base64(npy: Base64) -> ndarray:
	if len(npy) > MAX_NPY_BASE64_LENGTH:
		raise ValueError("array file is too large")
	bs = base64.b64decode(npy)
	if len(bs) > MAX_NPY_BYTES:
		raise ValueError("array file is too large")
	with BytesIO(bs) as io:
		# Check allocation metadata before np.load; a tiny file can declare a huge array
		version = np.lib.format.read_magic(io)
		if version == (1, 0):
			shape, _, dtype = np.lib.format.read_array_header_1_0(io)
		elif version == (2, 0):
			shape, _, dtype = np.lib.format.read_array_header_2_0(io)
		elif version == (3, 0):
			raise ValueError("NPY format version 3.0 is not supported")
		else:
			raise ValueError("unsupported array format")
		if not isinstance(shape, tuple) or any(not isinstance(n, int) or n < 0 for n in shape):
			raise ValueError("invalid array shape")
		size = prod(shape) * dtype.itemsize
		if dtype.hasobject or size > MAX_NPY_BYTES * 2:
			raise ValueError("invalid array size or dtype")
		io.seek(0)
		# Deserialize an array
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

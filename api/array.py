import base64
import numpy as np
from io import BytesIO
from api.types import Base64
from api.exceptions.client import ArrayValidationException

def to_npy_base64(array: np.ndarray) -> Base64:
	io = BytesIO()
	np.save(io, array, allow_pickle=False)
	seq = io.getvalue()
	string = base64.b64encode(seq).decode("ascii")
	return string

def from_npy_base64(npy: Base64) -> np.ndarray:
	bs = base64.b64decode(npy)
	obj = np.load(bs, allow_pickle=False)
	return obj

def validate_array(array: np.ndarray) -> bool:
	return True

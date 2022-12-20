from fastapi import APIRouter
from api import models
from api.image import to_png_base64

router = APIRouter(tags=["generation"])

@router.get("/{model}/random")
def generate(model: str, psi: float = 1.0):
	return {}

@router.get("/{model}/generate")
def generate(model: str, psi: float=1.0):
	m = models[model]
	z, w, y = m.generate_image(psi=psi)
	return {
		"hash": 0,
		"time": 1,
		"label": "",
		"width": m.width,
		"height": m.height,
		"data": to_png_base64(y)
	}

@router.post("/{model}/generate")
def generate(model: str, psi: float=1.0):
	m = models[model]
	z, w, y = m.generate_image(psi=psi)
	return {
		"hash": 0,
		"time": 1,
		"label": "",
		"width": m.width,
		"height": m.height,
		"data": to_png_base64(y)
	}

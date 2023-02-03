from fastapi import APIRouter, HTTPException, Path, Query
from api import models
from api.image import to_png_base64

router = APIRouter(tags=["generation"])

from api.exceptions import  NotFoundException,  raises

@router.get("/{model}/random", summary="Create an item", responses={})
def generate(model: str, psi: float = 1.0):
	pass

@router.get("/{model_id}/generate", responses=raises(NotFoundException))
def generate(model_id: str, psi: float=Query(default=1.0, gt=0)):
	model = models.get(model_id)
	if model is None:
		raise ModuleNotFoundError(model_id)
	z, w, y = model.generate_image(psi=psi)
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

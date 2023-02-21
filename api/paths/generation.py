from asyncio import to_thread
from fastapi import APIRouter, Query, Depends
from api import models
from api.image import to_png_base64
from api.exceptions import  NotFoundException, raises
from api.limit import SpeedLimit, limit

router = APIRouter(tags=["generation"], dependencies=[Depends(limit)])

@router.post("/{model_id}/generate", responses=raises(NotFoundException))
async def generate(model_id: str, psi: float=Query(default=1.0, gt=0)):
	model = models.get(model_id)
	if model is None:
		raise ModuleNotFoundError(model_id)
	async with SpeedLimit():
		await to_thread()
		z, w, y = model.generate_image(psi=psi)
	return {
		"hash": 0,
		"time": 1,
		"label": d,
		"width": model.width,
		"height": model.height,
		"data": to_png_base64(y)
	}

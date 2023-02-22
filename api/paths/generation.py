from asyncio import to_thread
from fastapi import APIRouter, Query, Depends
from api import models
from api.schemas import SimpleImage
from api.exceptions import  NotFoundException, raises
from api.limit import SpeedLimit, limit

router = APIRouter(tags=["generation"], dependencies=[Depends(limit)])

@router.post("/{model_id}/generate", response_model=SimpleImage, responses=raises(NotFoundException))
async def generate(model_id: str, psi: float=Query(default=1.0, gt=0)):
	if (model := models.get(model_id)) is None:
		raise ModuleNotFoundError(model_id)
	async with SpeedLimit():
		latent, style, image, label = await to_thread(
			model.generate_encoded,
			psi=psi
		)
	return SimpleImage(
		model_id=model_id,
		conditional=model.conditional,
		width=model.width,
		height=model.height,
		mime_type=model.image_type,
		data=image,
		label=label,
		latent=latent,
		style=style,
	)

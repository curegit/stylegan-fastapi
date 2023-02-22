from asyncio import to_thread
from fastapi import APIRouter, Query, Depends
from api import models
from api.array import to_npy_base64
from api.image import to_png_base64, to_jpeg_base64, png_mime_type, jpeg_mime_type
from api.schemas import SimpleImage
from api.exceptions import  NotFoundException, raises
from api.limit import SpeedLimit, limit

router = APIRouter(tags=["generation"], dependencies=[Depends(limit)])

@router.post("/{model_id}/generate", response_model=SimpleImage, responses=raises(NotFoundException))
async def generate(model_id: str, psi: float=Query(default=1.0, gt=0)):
	if (model := models.get(model_id)) is None:
		raise ModuleNotFoundError(model_id)
	async with SpeedLimit():
		latent, style, mime, image, label = await to_thread(
			model.generate_encoded,
			psi=psi
		)


	return SimpleImage(
		model_id=model_id,
		conditional=model.info.conditional,
		width=model.info.width,
		height=model.info.height,
		mime_type=model.image_mime_type,
		data=image,
		label=label,
		latent=to_npy_base64(),
		style=to_npy_base64(),
	)

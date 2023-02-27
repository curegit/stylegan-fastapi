from asyncio import to_thread
from fastapi import APIRouter, Query, Depends
from api.schemas import SimpleImage
from api.exceptions import responses
from api.exceptions.client import NotFoundException
from api.limit import SpeedLimit
from api.model import GeneratorModel
from api.operations.parameters import model, label
from api.operations.dependencies import limit

router = APIRouter(tags=["generation"], dependencies=[Depends(limit)], responses=responses())


@router.post("/{model_id}/generate", response_model=SimpleImage, responses=responses())
async def generate(model: GeneratorModel = Depends(model), psi: float = Query(default=1.0, gt=0)):
	async with SpeedLimit():
		latent, style, image, label = await to_thread(
			model.generate_encoded,
			psi=psi,
		)
	return SimpleImage(
		model_id=model.id,
		conditional=model.conditional,
		width=model.width,
		height=model.height,
		mime_type=model.image_type,
		data=image,
		label=label,
		latent=latent,
		style=style,
	)


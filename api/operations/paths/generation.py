from asyncio import to_thread
from fastapi import APIRouter, Depends
from api.schemas import SimpleImage
from api.exceptions import raises_from, responses
from api.exceptions.client import NotFoundException, ModelNotFoundException, ArrayValidationException
from api.limit import SpeedLimit
from api.model import GeneratorModel
from api.operations.parameters import model, label, psi, latent, sd
from api.operations.dependencies import limit

router = APIRouter(tags=["generation"], dependencies=[Depends(limit)], responses=responses(*raises_from(limit)))


@router.post(
	"/{model_id}/generate",
	operation_id="generate",
	response_model=SimpleImage,
	responses=responses(*raises_from(model, label))
)
async def generate(
	model: GeneratorModel = Depends(model),
	label: str | None = Depends(label),
	psi: float = Depends(psi),
	sd = Depends(sd),
):
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


@router.post(
	"/{model_id}/regenerate",
	response_model=SimpleImage,
	responses=responses(*raises_from(model, label, latent))
)
async def regenerate(
	model: GeneratorModel = Depends(model),
	label: str | None = Depends(label),
	psi: float = Depends(psi),
	latent = Depends(latent),
	sd = Depends(sd),
):
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


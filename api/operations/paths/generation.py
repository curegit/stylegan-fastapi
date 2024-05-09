from asyncio import to_thread
from numpy import ndarray
from fastapi import APIRouter, Depends
from api.schemas import SimpleImage
from api.limit import SpeedLimit
from api.model import GeneratorModel
from api.exceptions import raises_from, responses
from api.operations.parameters import model, optional_label, psi, optional_latent, sd
from api.operations.dependencies import limit

router = APIRouter(tags=["generation"], dependencies=[Depends(limit)], responses=responses(*raises_from(limit)))

@router.post("/{model_id}/generate", operation_id="generate", response_model=SimpleImage, responses=responses(*raises_from(model, optional_label, optional_latent)))
async def generate(
	model: GeneratorModel = Depends(model),
	label: tuple[str, int] | None = Depends(optional_label),
	psi: float = Depends(psi),
	latent: ndarray | None = Depends(optional_latent),
	sd: float = Depends(sd),
):
	async with SpeedLimit():
		latent_str, style, image, label_str = await to_thread(
			model.generate_encoded,
			category=(None if label is None else label[1]),
			psi=psi,
			mean=latent,
			sd=sd,
		)
	return SimpleImage(
		model_id=model.id,
		width=model.width,
		height=model.height,
		mime_type=model.image_type,
		data=image,
		label=label_str,
		latent=latent_str,
		style=style,
	)

from asyncio import to_thread
from numpy import ndarray
from fastapi import APIRouter, Depends
from api.schemas import SimpleImage, CompoundImage
from api.limit import SpeedLimit
from api.model import GeneratorModel
from api.exceptions import raises_from, responses
from api.operations.parameters import model, styles
from api.operations.dependencies import limit

router = APIRouter(tags=["manipulation"], dependencies=[Depends(limit)], responses=responses(*raises_from(limit)))

@router.post("/{model_id}/blend", operation_id="blend", response_model=SimpleImage, responses=responses(*raises_from(model, styles)))
async def blend(model: GeneratorModel = Depends(model), styles: list[ndarray] = Depends(styles)):
	"""
	Blends (averages) multiple styles into a single image using the specified model.

	Returns a SimpleImage object containing the blended image and style information.
	"""
	async with SpeedLimit():
		style_str, image = await to_thread(
			model.combine_styles_encoded,
			styles,
		)
	return SimpleImage(
		model=model.id,
		width=model.width,
		height=model.height,
		mimeType=model.image_type,
		data=image,
		style=style_str
	)

@router.post("/{model_id}/mix", operation_id="mix", response_model=CompoundImage, responses=responses(*raises_from(model, styles)))
async def mix(model: GeneratorModel = Depends(model), styles: list[ndarray] = Depends(styles)):
	"""
	Mixes multiple styles into a single image using the specified model.

	Returns a CompoundImage object containing the mixed image and styles information.
	"""
	async with SpeedLimit():
		styles_str, image = await to_thread(
			model.mix_styles_encoded,
			styles,
		)
	return CompoundImage(
		model=model.id,
		width=model.width,
		height=model.height,
		mimeType=model.image_type,
		data=image,
		styles=styles_str,
	)

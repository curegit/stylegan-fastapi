from fastapi import Path, Query, Body, Depends
from api import models
from api.array import from_npy_base64, validate_array, clamp_array
from api.model import GeneratorModel
from api.schemas.request import RegenerateRequest
from api.exceptions import raises, raises_from
from api.exceptions.client import NotFoundException, LabelNotFoundException, DeserializationException, ArrayValidationException

@raises(NotFoundException)
async def model(model_id: str = Path(min_length=1)):
	if (model := models.get(model_id)) is None:
		raise NotFoundException()
	return model

@raises(LabelNotFoundException, *raises_from(model))
async def label(label: str | None = Query(None, min_length=1), model: GeneratorModel = Depends(model)) -> str | None:
	if label is None:
		return None
	elif not model.conditional:
		raise LabelNotFoundException()
	elif label not in model.labels:
		raise LabelNotFoundException()
	return label

async def psi(psi: float = Query(1.0, gt=0, le=2)):
	return psi

async def sd(sd: float = Query(1.0, gt=0, le=2)):
	return sd

@raises(DeserializationException, ArrayValidationException, *raises_from(model))
async def latent(latent: RegenerateRequest | None = Body(None), model: GeneratorModel = Depends(model)):
	if latent is None:
		return None
	try:
		arr = from_npy_base64(latent)
	except:
		raise DeserializationException()
	if not validate_array(arr):
		raise ArrayValidationException()
	return clamp_array(arr, -100, 100, replace_nan=True)

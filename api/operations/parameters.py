from numpy import ndarray, float32
from fastapi import Path, Query, Body, Depends
from api import models
from api.array import from_npy_base64, validate_array, clamp_array
from api.model import GeneratorModel
from api.schemas.request import GenerateRequestBody, ReconstructionRequestBody
from api.exceptions import raises, raises_from
from api.exceptions.client import ModelNotFoundException, LabelNotFoundException, DeserializationException, ArrayValidationException

@raises(ModelNotFoundException)
async def model(model_id: str = Path(min_length=1)) -> GeneratorModel:
	if (model := models.get(model_id)) is None:
		raise ModelNotFoundException(model_id)
	return model

@raises(LabelNotFoundException, *raises_from(model))
async def optional_label(label: str | None = Query(None, min_length=1), model: GeneratorModel = Depends(model)) -> tuple[str, int] | None:
	if label is None:
		return None
	elif not model.conditional:
		raise LabelNotFoundException(label)
	elif label not in model.labels:
		raise LabelNotFoundException(label)
	return label, model.generator.lookup_label(label)

async def psi(psi: float = Query(1.0, gt=0, le=2)) -> float:
	return psi

async def sd(sd: float = Query(1.0, gt=0, le=2)) -> float:
	return sd

@raises(DeserializationException, ArrayValidationException, *raises_from(model))
async def optional_latent(req: GenerateRequestBody | None = Body(None), model: GeneratorModel = Depends(model)) -> ndarray | None:
	if req is None or req.latent is None:
		return None
	try:
		arr = from_npy_base64(req.latent)
	except Exception:
		raise DeserializationException()
	if not validate_array(arr, shape=(model.generator.size,), dtype=float32):
		raise ArrayValidationException()
	return clamp_array(arr, -100, 100, replace_nan=True)

@raises(DeserializationException, ArrayValidationException, *raises_from(model))
async def styles(req: ReconstructionRequestBody = Body(), model: GeneratorModel = Depends(model)) -> list[ndarray]:
	res = []
	for style in req.styles:
		try:
			arr = from_npy_base64(style)
		except Exception:
			raise DeserializationException()
		if not validate_array(arr, shape=(model.generator.size,), dtype=float32):
			raise ArrayValidationException()
		array = clamp_array(arr, -100, 100, replace_nan=True)
		res.append(array)
	return res

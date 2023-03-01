from fastapi import Path, Query, Depends
from api import models
from api.model import GeneratorModel
from api.exceptions import raises, raises_from
from api.exceptions.client import NotFoundException, LabelNotFoundException

@raises(NotFoundException)
async def model(model_id: str = Path(min_length=1)):
	if (model := models.get(model_id)) is None:
		raise NotFoundException
	return model

@raises(LabelNotFoundException, *raises_from(model))
async def label(label: str | None = Query(min_length=1), model: GeneratorModel = Depends(model)) -> str | None:
	if label is None:
		return None
	elif not model.conditional:
		raise
	elif label not in model.labels:
		raise LabelNotFoundException()
	return label

async def psi():
	pass

async def latent(model: GeneratorModel = Depends(model)):
	pass


async def model(model_id: str = Path(min_length=1)):
	if (model := models.get(model_id)) is None:
		raise NotFoundException
	return model

async def label(label: str | None = Query(min_length=1), model: GeneratorModel = Depends(model)) -> str | None:
	if label is None:
		return None
	elif not model.conditional:
		raise
	elif label not in model.labels:
		raise
	return label

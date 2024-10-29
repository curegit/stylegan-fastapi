from fastapi import APIRouter
from api import config, models
from api.schemas import Model

router = APIRouter(tags=["info"])

@router.get("/", operation_id="root", response_model=str)
async def welcome():
	"""
	Returns a simple hello world message.
	"""
	return "Hello"

@router.get("/version", operation_id="version", response_model=str)
async def version():
	"""
	Returns the current version of the application.
	"""
	return config.version

@router.get("/models/", operation_id="models", response_model=list[Model])
async def model_list():
	"""
	Returns a list of all available models with their information.
	"""
	return [model.info for model in models.values()]

from fastapi import APIRouter
from api import models
from api.schemas import Model

router = APIRouter(tags=["info"])

@router.get("/", operation_id="root", response_model=str)
async def welcome():
	"""
	hello world message
	"""
	return "Hello"

@router.get("/models/", response_model=list[Model])
async def model_list():
	return [model.info for model in models.values()]

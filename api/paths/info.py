from fastapi import APIRouter
from api import models
from api.schemas.model import Model

router = APIRouter(tags=["info"])

@router.get("/")
def hello():
	return {"": ""}

@router.get("/list")
def model_list():
	return {key: model.name for key, model in models.items()}

@router.get("/models", response_model=dict[str, Model])
def model_specs():
	return {key: model.spec_dict for key, model in models.items()}

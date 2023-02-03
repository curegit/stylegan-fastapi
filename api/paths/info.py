from fastapi import APIRouter
from api import models
from api.schemas import Model

router = APIRouter(tags=["info"])

@router.get("/")
def hello():
	return {"": ""}

@router.get("/models/", response_model=list[Model])
def model_specs():
	return [model.spec for model in models.values()]

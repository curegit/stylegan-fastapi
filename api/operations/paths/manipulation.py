from fastapi import APIRouter
from api.schemas.image import SimpleImage, CompoundImage

router = APIRouter(tags=["manipulation"])

@router.post("/{model}/blend", response_model=SimpleImage)
def blend(model: str):
	pass

@router.post("/{model}/mix", response_model=CompoundImage)
def mix(model: str):
	pass

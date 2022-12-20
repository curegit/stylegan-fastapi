from fastapi import APIRouter

router = APIRouter(tags=["manipulation"])

@router.post("/{model}/blend")
def blend(model: str):
	pass

@router.post("/{model}/mix")
def mix(model: str):
	pass

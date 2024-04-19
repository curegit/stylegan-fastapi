from asyncio import to_thread
from fastapi import APIRouter, Depends
from api.schemas.image import SimpleImage, CompoundImage
from api.exceptions.server import BadGatewayException
from api.exceptions.server import OverloadedException
from api.limit import SpeedLimit
from api.model import GeneratorModel
from api.exceptions import raises_from, responses
from api.operations.parameters import model
from api.operations.dependencies import limit

router = APIRouter(tags=["manipulation"], dependencies=[Depends(limit)], responses=responses(*raises_from(limit)))

@router.post("/{model_id}/blend", response_model=SimpleImage, responses=responses(*raises_from(model)))
async def blend(model: GeneratorModel = Depends(model)):
	async with SpeedLimit():
		raise BadGatewayException()

@router.post("/{model_id}/mix", operation_id="mix", response_model=CompoundImage, responses=responses(*raises_from(model)))
async def mix(model: GeneratorModel = Depends(model)):
	async with SpeedLimit():
		styles, image, label = await to_thread()
	return CompoundImage()

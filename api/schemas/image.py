from pydantic import BaseModel, Field
from api.types import base64

class Image(BaseModel):
	model_id: str = Field(min_length=1, example="animal")
	conditional: bool = Field(example=True)
	width: int = Field(ge=1, example=256)
	height: int = Field(ge=1, example=256)
	data: base64

class SimpleImage(Image):
	label: str | None = Field(example="Cat")
	latent: base64

class CompoundImage(Image):
	styles: list[base64]

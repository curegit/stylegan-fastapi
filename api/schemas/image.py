from pydantic import BaseModel, Field
from api.image import png_mime_type
from api.types import Base64, base64_examples

class Image(BaseModel):
	model_id: str = Field(min_length=1, example="animal")
	conditional: bool = Field(example=True)
	width: int = Field(ge=1, example=256)
	height: int = Field(ge=1, example=256)
	mime_type: str = Field(example=png_mime_type)
	data: Base64 = Field(example=next(base64_examples))

class SimpleImage(Image):
	label: str | None = Field(example="Cat")
	latent: Base64 = Field(example=next(base64_examples))
	style: Base64 = Field(example=next(base64_examples))

class CompoundImage(Image):
	styles: list[Base64] = Field(min_items=1, example=([next(base64_examples)] * 4 + [next(base64_examples)] * 3))

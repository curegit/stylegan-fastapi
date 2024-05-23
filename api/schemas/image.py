from pydantic import BaseModel, Field
from api.image import png_mime_type
from api.types import Base64, base64_examples

class Image(BaseModel):
	model: str = Field(min_length=1, examples=["animal"])
	width: int = Field(ge=1, examples=[256])
	height: int = Field(ge=1, examples=[256])
	mimeType: str = Field(examples=[png_mime_type])
	data: Base64 = Field(examples=[next(base64_examples)])


class SimpleImage(Image):
	style: Base64 = Field(examples=[next(base64_examples)])


class SimplePureImage(SimpleImage):
	label: str | None = Field(examples=["Cat"])
	latent: Base64 = Field(examples=[next(base64_examples)])


class CompoundImage(Image):
	styles: list[Base64] = Field(min_length=1, examples=[([next(base64_examples)] * 4 + [next(base64_examples)] * 3)])

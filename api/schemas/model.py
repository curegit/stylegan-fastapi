from pydantic import BaseModel, Field
from api.image import png_mime_type

class Model(BaseModel):
	id: str = Field(min_length=1, examples=["animal"])
	name: str = Field(examples=["My Animal Model"])
	description: str
	conditional: bool = Field(examples=[True])
	labels: list[str] | None = Field(min_length=1, examples=[["Cat", "Dog", "Unicorn"]])
	width: int = Field(ge=1, examples=[256])
	height: int = Field(ge=1, examples=[256])
	lossy: bool = Field(examples=[False])
	mime_type: str = Field(examples=[png_mime_type])

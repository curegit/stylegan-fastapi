from pydantic import BaseModel, Field

class ImageBase(BaseModel):
	model_id: str = Field("", example="")
	model_name: str
	width: int
	height: int
	conditional: bool

class Image(ImageBase):
	latent_npy: str
	style_npy: str
	label: list[str] | None
	body: str

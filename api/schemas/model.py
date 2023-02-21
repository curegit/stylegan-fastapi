from pydantic import BaseModel, Field

class Model(BaseModel):
	id: str = Field(min_length=1, example="animal")
	name: str = Field(example="My Animal Model")
	description: str
	conditional: bool = Field(example=True)
	labels: list[str] | None = Field(min_items=1, unique_items=True, example=["Cat", "Dog", "Unicorn"])
	width: int = Field(ge=1, example=256)
	height: int = Field(ge=1, example=256)

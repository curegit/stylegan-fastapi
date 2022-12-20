from pydantic import BaseModel, Field

class Model(BaseModel):
	key: str
	name: str
	description: str
	conditional: bool
	labels: list[str] | None
	width: int
	height: int

import uuid

from pydantic import BaseModel, Field


class TaskModel(BaseModel):
    id: uuid.UUID
    status: str = Field(max=30)
    hasCat: bool
    cats: list[CatModel]


class CatModel(BaseModel):
    id: uuid.UUID
    catName: str = Field(min=1, max=10)
    catImageUrl: str

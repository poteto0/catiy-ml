import uuid
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_snake


class TaskModel(BaseModel):
    id: uuid.UUID
    status: str = Field(max=30)
    hasCat: bool
    cats: list[CatModel]


class CatModel(BaseModel):
    id: uuid.UUID
    catName: str = Field(min=1, max=10)
    catImageUrl: str


LabelStr = Annotated[
    str,
    Field(min_length=1, max_length=100),
]

ClipRequestLabels = Annotated[
    list[LabelStr],
    Field(min_length=1, max_length=20),
]


class ClipResult(BaseModel):
    label: LabelStr
    prob: float

    def __lt__(self, other: ClipResult) -> bool:
        return self.prob < other.prob


class ClipResponse(BaseModel):
    mostLikelyLabel: LabelStr
    results: list[ClipResult]


class CatClassifyRequest(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_snake,
        populate_by_name=True,
    )

    taskId: uuid.UUID


class ClassifyResultUnit(BaseModel):
    idx: int
    label: str | None
    prob: float

    def __lt__(self, other: ClassifyResultUnit) -> bool:
        return self.prob < other.prob


class ClassifyResult(BaseModel):
    mostLikely: ClassifyResultUnit
    results: list[ClassifyResultUnit]

import uuid

from app.ents import Task


def init_task() -> Task:
    return Task(
        id=uuid.uuid4(),
        status="draft",
        has_cat=False,
    )

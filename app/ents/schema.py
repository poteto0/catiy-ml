import uuid

from sqlalchemy import Boolean, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.ents.base import Base


class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    status: Mapped[str] = mapped_column(String, default="draft")
    has_cat: Mapped[bool] = mapped_column(Boolean, default=False)
    cats: Mapped[list[Cat]] = relationship("Cat", back_populates="task")


class Cat(Base):
    __tablename__ = "cats"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    cat_name: Mapped[str] = mapped_column(String)
    cat_image_url: Mapped[str] = mapped_column(String)
    task_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tasks.id"),
    )
    task: Mapped[Task] = relationship("Task", back_populates="cats")

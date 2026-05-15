from datetime import datetime
from enum import Enum
from pydantic import BaseModel, ConfigDict


class CaseStatus(str, Enum):
    open = "open"
    in_progress = "in_progress"
    closed = "closed"


class CasePriority(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"


class TaskStatus(str, Enum):
    open = "open"
    closed = "closed"


class Task(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    case_id: int
    title: str
    status: TaskStatus = TaskStatus.open
    created_at: datetime
    updated_at: datetime


class TaskUpdate(BaseModel):
    title: str | None = None
    status: TaskStatus | None = None


class CaseBase(BaseModel):
    title: str
    about: str
    priority: CasePriority = CasePriority.medium


class CaseCreate(CaseBase):
    pass


class CaseUpdate(BaseModel):
    title: str | None = None
    about: str | None = None
    priority: CasePriority | None = None
    status: CaseStatus | None = None


class Case(CaseBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    status: CaseStatus = CaseStatus.open
    tasks: list[Task] = []
    created_at: datetime
    updated_at: datetime

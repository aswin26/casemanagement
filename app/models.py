from datetime import datetime
from enum import Enum
from pydantic import BaseModel


class CaseStatus(str, Enum):
    open = "open"
    in_progress = "in_progress"
    closed = "closed"


class CasePriority(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"


class CaseBase(BaseModel):
    title: str
    description: str
    priority: CasePriority = CasePriority.medium


class CaseCreate(CaseBase):
    pass


class CaseUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    priority: CasePriority | None = None
    status: CaseStatus | None = None


class Case(CaseBase):
    id: int
    status: CaseStatus = CaseStatus.open
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

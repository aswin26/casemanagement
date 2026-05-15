from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException
from app.models import Case, CaseCreate, CaseUpdate, CaseStatus, CasePriority

router = APIRouter(prefix="/cases", tags=["cases"])

# In-memory store for now; replace with DB later
_cases: dict[int, dict] = {}
_next_id = 1


@router.get("/", response_model=list[Case])
def list_cases():
    return [Case(**c) for c in _cases.values()]


@router.post("/", response_model=Case, status_code=201)
def create_case(payload: CaseCreate):
    global _next_id
    now = datetime.now(timezone.utc)
    case = {
        "id": _next_id,
        "title": payload.title,
        "description": payload.description,
        "priority": payload.priority,
        "status": CaseStatus.open,
        "created_at": now,
        "updated_at": now,
    }
    _cases[_next_id] = case
    _next_id += 1
    return Case(**case)


@router.get("/{case_id}", response_model=Case)
def get_case(case_id: int):
    if case_id not in _cases:
        raise HTTPException(status_code=404, detail="Case not found")
    return Case(**_cases[case_id])


@router.patch("/{case_id}", response_model=Case)
def update_case(case_id: int, payload: CaseUpdate):
    if case_id not in _cases:
        raise HTTPException(status_code=404, detail="Case not found")
    case = _cases[case_id]
    updates = payload.model_dump(exclude_unset=True)
    case.update(updates)
    case["updated_at"] = datetime.now(timezone.utc)
    return Case(**case)


@router.delete("/{case_id}", status_code=204)
def delete_case(case_id: int):
    if case_id not in _cases:
        raise HTTPException(status_code=404, detail="Case not found")
    del _cases[case_id]

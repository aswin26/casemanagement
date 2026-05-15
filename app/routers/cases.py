from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException
from app.models import Case, CaseCreate, CaseUpdate, CaseStatus, Task, TaskStatus, TaskUpdate

router = APIRouter(prefix="/cases", tags=["cases"])

# In-memory stores; replace with DB later
_cases: dict[int, dict] = {}
_tasks: dict[int, dict] = {}
_next_case_id = 1
_next_task_id = 1


def _case_with_tasks(case_id: int) -> Case:
    case = _cases[case_id]
    tasks = [Task(**t) for t in _tasks.values() if t["case_id"] == case_id]
    return Case(**{**case, "tasks": tasks})


@router.get("/", response_model=list[Case])
def list_cases():
    return [_case_with_tasks(cid) for cid in _cases]


@router.post("/", response_model=Case, status_code=201)
def create_case(payload: CaseCreate):
    global _next_case_id, _next_task_id
    now = datetime.now(timezone.utc)

    case = {
        "id": _next_case_id,
        "title": payload.title,
        "about": payload.about,
        "priority": payload.priority,
        "status": CaseStatus.open,
        "created_at": now,
        "updated_at": now,
    }
    _cases[_next_case_id] = case

    # Auto-create one open task for every new case
    task = {
        "id": _next_task_id,
        "case_id": _next_case_id,
        "title": "Initial review",
        "status": TaskStatus.open,
        "created_at": now,
        "updated_at": now,
    }
    _tasks[_next_task_id] = task

    _next_case_id += 1
    _next_task_id += 1

    return _case_with_tasks(case["id"])


@router.get("/{case_id}", response_model=Case)
def get_case(case_id: int):
    if case_id not in _cases:
        raise HTTPException(status_code=404, detail="Case not found")
    return _case_with_tasks(case_id)


@router.patch("/{case_id}", response_model=Case)
def update_case(case_id: int, payload: CaseUpdate):
    if case_id not in _cases:
        raise HTTPException(status_code=404, detail="Case not found")
    updates = payload.model_dump(exclude_unset=True)
    _cases[case_id].update(updates)
    _cases[case_id]["updated_at"] = datetime.now(timezone.utc)
    return _case_with_tasks(case_id)


@router.delete("/{case_id}", status_code=204)
def delete_case(case_id: int):
    if case_id not in _cases:
        raise HTTPException(status_code=404, detail="Case not found")
    # Remove associated tasks
    task_ids = [tid for tid, t in _tasks.items() if t["case_id"] == case_id]
    for tid in task_ids:
        del _tasks[tid]
    del _cases[case_id]


# --- Task sub-routes ---

@router.get("/{case_id}/tasks", response_model=list[Task])
def list_tasks(case_id: int):
    if case_id not in _cases:
        raise HTTPException(status_code=404, detail="Case not found")
    return [Task(**t) for t in _tasks.values() if t["case_id"] == case_id]


@router.patch("/{case_id}/tasks/{task_id}", response_model=Task)
def update_task(case_id: int, task_id: int, payload: TaskUpdate):
    if case_id not in _cases:
        raise HTTPException(status_code=404, detail="Case not found")
    if task_id not in _tasks or _tasks[task_id]["case_id"] != case_id:
        raise HTTPException(status_code=404, detail="Task not found")
    updates = payload.model_dump(exclude_unset=True)
    _tasks[task_id].update(updates)
    _tasks[task_id]["updated_at"] = datetime.now(timezone.utc)
    return Task(**_tasks[task_id])

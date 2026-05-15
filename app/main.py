from fastapi import FastAPI
from app.routers import cases

app = FastAPI(title="Case Management API", version="0.1.0")

app.include_router(cases.router)


@app.get("/health")
def health():
    return {"status": "ok"}

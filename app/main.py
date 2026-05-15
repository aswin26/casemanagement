import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.routers import cases

app = FastAPI(title="Case Management API", version="0.1.0")

app.include_router(cases.router)


@app.get("/health")
def health():
    return {"status": "ok"}


# Serve React frontend — only when the build output exists
_dist = os.path.join(os.path.dirname(__file__), "..", "frontend", "dist")
if os.path.isdir(_dist):
    app.mount("/assets", StaticFiles(directory=os.path.join(_dist, "assets")), name="assets")

    @app.get("/{full_path:path}", include_in_schema=False)
    def serve_spa(full_path: str):
        return FileResponse(os.path.join(_dist, "index.html"))

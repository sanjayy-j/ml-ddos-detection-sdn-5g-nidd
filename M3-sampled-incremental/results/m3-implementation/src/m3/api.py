from pathlib import Path

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from m3.store import RunRepository


def create_app(root="output/runs"):
    app = FastAPI(title="M3 experimental results", version="0.1.0")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
        allow_methods=["GET"],
        allow_headers=["*"],
    )
    repository = RunRepository(root)

    @app.get("/api/health")
    def health():
        return {"status": "ok", "schema_version": 1}

    @app.get("/api/runs")
    def runs():
        return {"runs": repository.list()}

    @app.get("/api/overview")
    def overview():
        all_runs = repository.list()
        completed = [r for r in all_runs if r["status"] == "completed"]
        candidates = [r for r in completed if r["metrics"].get("f1", {}).get("value") is not None]
        best = max(candidates, key=lambda r: r["metrics"]["f1"]["value"], default=None)
        return {
            "total_runs": len(all_runs),
            "completed_runs": len(completed),
            "running_runs": sum(r["status"] == "running" for r in all_runs),
            "failed_runs": sum(r["status"] == "failed" for r in all_runs),
            "best_run_id": best["run_id"] if best else None,
        }

    @app.get("/api/runs/{run_id}")
    def run(run_id: str):
        try:
            return repository.get(run_id)
        except FileNotFoundError as exc:
            raise HTTPException(404, str(exc)) from exc

    @app.get("/api/runs/{run_id}/series")
    def series(run_id: str, limit: int = Query(1000, ge=2, le=10000)):
        try:
            return repository.series(run_id, limit)
        except FileNotFoundError as exc:
            raise HTTPException(404, str(exc)) from exc

    # A frontend production build is optional; API remains usable without Node.
    frontend = Path(__file__).resolve().parents[2] / "frontend" / "dist"
    if frontend.is_dir():
        from fastapi.staticfiles import StaticFiles

        app.mount("/", StaticFiles(directory=frontend, html=True), name="dashboard")
    return app


app = create_app()

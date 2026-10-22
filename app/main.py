from __future__ import annotations

import json
import sys
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from eso_agent.audit import build_audit, render_audit_html  # noqa: E402
from eso_agent.backtest import gallery_index, run_gallery  # noqa: E402
from eso_agent.brief import render_brief_html  # noqa: E402
from eso_agent.catalog import architecture_payload  # noqa: E402
from eso_agent.document import render_ts_html  # noqa: E402
from eso_agent.engine import (  # noqa: E402
    RUNS,
    batch_queue,
    batching,
    list_runs,
    rerun_from,
    resume,
    samples_public,
    scenarios_public,
    snapshot,
    start_queue_case,
    start_run,
    subscribe,
)
from eso_agent.graph import mermaid  # noqa: E402
from eso_agent.llm import llm_mode  # noqa: E402
from eso_agent.network import load_network  # noqa: E402
from eso_agent.queue import queue_public, reset_queue  # noqa: E402

app = FastAPI(title="ESO prijungimo sąlygos", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class StartBody(BaseModel):
    scenario_id: str | None = None
    text: str = ""
    form: dict = Field(default_factory=dict)


class ResumeBody(BaseModel):
    decision: str = "approve"
    section3: str | None = None
    force: bool = False
    override_reason: str | None = None


class RerunBody(BaseModel):
    from_tool: str
    overrides: dict = Field(default_factory=dict)


@app.get("/api/health")
def health():
    return {"ok": True, "llm_mode": llm_mode(), "batching": batching()}


@app.get("/api/scenarios")
def scenarios():
    return scenarios_public()


@app.get("/api/samples")
def samples():
    return samples_public()


@app.get("/api/architecture")
def architecture():
    payload = architecture_payload()
    payload["mermaid"] = mermaid()
    return payload


@app.get("/api/network")
def network():
    return load_network()


@app.get("/api/queue")
def queue_get():
    payload = queue_public()
    payload["batching"] = batching()
    return payload


@app.post("/api/queue/reset")
def queue_reset():
    reset_queue()
    return queue_public()


@app.post("/api/queue/batch")
async def queue_batch():
    return await batch_queue()


@app.post("/api/queue/{cid}/start")
async def queue_start(cid: str):
    try:
        return await start_queue_case(cid, wait=False)
    except KeyError as exc:
        raise HTTPException(404, f"queue case {cid} not found") from exc


@app.get("/api/gallery")
def gallery_get():
    return gallery_index()


@app.post("/api/gallery/run")
def gallery_run():
    return run_gallery()


@app.get("/api/runs")
def runs():
    return list_runs()


@app.post("/api/runs")
async def create(body: StartBody):
    form = body.form or None
    return await start_run(body.scenario_id, body.text, form)


@app.get("/api/runs/{rid}")
def get_run(rid: str):
    if rid not in RUNS:
        raise HTTPException(404)
    return snapshot(RUNS[rid])


@app.get("/api/runs/{rid}/events")
async def events(rid: str):
    if rid not in RUNS:
        raise HTTPException(404)

    async def gen():
        async for ev in subscribe(rid):
            payload = json.dumps(ev, ensure_ascii=False, default=str)
            yield f"event: {ev.get('type', 'message')}\ndata: {payload}\n\n"

    return StreamingResponse(gen(), media_type="text/event-stream", headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})


@app.post("/api/runs/{rid}/resume")
async def resume_run(rid: str, body: ResumeBody):
    if rid not in RUNS:
        raise HTTPException(404)
    try:
        return await resume(rid, body.decision, body.section3, body.force, body.override_reason)
    except ValueError as exc:
        raise HTTPException(400, str(exc)) from exc


@app.post("/api/runs/{rid}/rerun")
async def rerun(rid: str, body: RerunBody):
    if rid not in RUNS:
        raise HTTPException(404)
    return await rerun_from(rid, body.from_tool, body.overrides)


@app.get("/api/runs/{rid}/ts.html")
def ts_html(rid: str):
    if rid not in RUNS:
        raise HTTPException(404)
    return HTMLResponse(render_ts_html(snapshot(RUNS[rid])))


@app.get("/api/runs/{rid}/audit.json")
def audit_json(rid: str):
    if rid not in RUNS:
        raise HTTPException(404)
    return build_audit(RUNS[rid], snapshot(RUNS[rid]))


@app.get("/api/runs/{rid}/audit.html")
def audit_html(rid: str):
    if rid not in RUNS:
        raise HTTPException(404)
    return HTMLResponse(render_audit_html(build_audit(RUNS[rid], snapshot(RUNS[rid]))))


@app.get("/api/runs/{rid}/brief.html")
def brief_html(rid: str):
    if rid not in RUNS:
        raise HTTPException(404)
    snap = snapshot(RUNS[rid])
    if not (snap.get("escalate") or {}).get("brief"):
        raise HTTPException(404, "Stiprinimo paketo nėra — byla neeskaluota.")
    return HTMLResponse(render_brief_html(snap))


dist = ROOT / "web" / "dist"
if dist.exists():
    app.mount("/", StaticFiles(directory=dist, html=True), name="ui")
else:
    demo = ROOT / "demo"

    @app.get("/")
    def fallback():
        html = (demo / "dashboard.html").read_text(encoding="utf-8") if (demo / "dashboard.html").exists() else "<p>Build the web UI: cd web && npm install && npm run build</p>"
        return HTMLResponse(html)

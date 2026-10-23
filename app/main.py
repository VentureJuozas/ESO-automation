from __future__ import annotations

import json
import sys
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse, Response, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from eso_agent.audit import build_audit, render_audit_html  # noqa: E402
from eso_agent.backtest import gallery_index, run_gallery, run_gallery_whatif  # noqa: E402
from eso_agent.brief import brief_pdf_bytes, render_brief_html  # noqa: E402
from eso_agent.catalog import architecture_payload  # noqa: E402
from eso_agent.document import render_ts_html  # noqa: E402
from eso_agent.engine import (  # noqa: E402
    RUNS,
    batch_queue,
    batching,
    hydrate_runs,
    list_runs,
    rerun_from,
    reset_demo,
    resume,
    supply_data,
    whatif,
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

@asynccontextmanager
async def lifespan(_app: FastAPI):
    hydrate_runs()
    from eso_agent.queue import ensure_queue

    ensure_queue()
    yield


app = FastAPI(title="ESO prijungimo sąlygos", version="0.1.0", lifespan=lifespan)
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
    return {
        "ok": True,
        "llm_mode": llm_mode(),
        "batching": batching(),
        "offline": True,
        "persist": True,
    }


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


@app.post("/api/demo/reset")
def demo_reset():
    return reset_demo()


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


@app.post("/api/gallery/whatif")
def gallery_whatif():
    return run_gallery_whatif()


@app.get("/api/present")
def present_pack():
    from eso_agent.present import frozen_pack

    return frozen_pack()


@app.get("/api/adapters")
def adapters_get():
    from eso_agent.adapters import adapter_catalog, adapter_mode

    return {"mode": adapter_mode(), "adapters": adapter_catalog()}


@app.get("/api/onepager.html")
def onepager_html():
    from eso_agent.onepager import render_onepager_html

    return HTMLResponse(render_onepager_html())


@app.get("/api/onepager.pdf")
def onepager_pdf():
    from eso_agent.pdfutil import render_onepager_pdf

    return Response(render_onepager_pdf(), media_type="application/pdf", headers={"Content-Disposition": 'attachment; filename="onepager.pdf"'})


@app.get("/api/fonts/{name}")
def font_file(name: str):
    from eso_agent.fonts import FONT_DIR

    if name not in {"DejaVuSans.ttf", "DejaVuSans-Bold.ttf"}:
        raise HTTPException(404)
    path = FONT_DIR / name
    if not path.exists():
        raise HTTPException(404)
    return FileResponse(path, media_type="font/ttf")


class PortalSubmit(BaseModel):
    kw: float = 11
    phases: int = 3
    lat: float | None = None
    lon: float | None = None
    object_name: str = "Naujas buitinis objektas"
    address: str = ""


class PortalAnswer(BaseModel):
    lat: float | None = None
    lon: float | None = None
    kw: float | None = None
    phases: int | None = None
    text: str = ""


@app.post("/api/portal/applications")
def portal_submit(body: PortalSubmit):
    from eso_agent.portal import submit

    return submit(body.model_dump())


@app.get("/api/portal/applications/{aid}")
def portal_get(aid: str):
    from eso_agent.portal import get_app

    try:
        return get_app(aid)
    except KeyError as exc:
        raise HTTPException(404) from exc


@app.post("/api/portal/applications/{aid}/answer")
def portal_answer(aid: str, body: PortalAnswer):
    from eso_agent.portal import answer

    try:
        return answer(aid, body.model_dump(exclude_none=True))
    except KeyError as exc:
        raise HTTPException(404) from exc


@app.get("/api/portal/applications/{aid}/ts.html")
def portal_ts(aid: str):
    from eso_agent.portal import ts_html

    try:
        return HTMLResponse(ts_html(aid))
    except KeyError as exc:
        raise HTTPException(404) from exc


@app.get("/api/portal/applications/{aid}/ts.pdf")
def portal_pdf(aid: str):
    from eso_agent.portal import ts_pdf

    try:
        data = ts_pdf(aid)
    except KeyError as exc:
        raise HTTPException(404) from exc
    return Response(data, media_type="application/pdf", headers={"Content-Disposition": f'attachment; filename="{aid}.pdf"'})


class WhatIfBody(BaseModel):
    kw: float = 11
    phases: int = 3
    distance_m: float | None = None
    pending_kw: float = 0
    lat: float | None = None
    lon: float | None = None
    existing_kw: float = 0
    text: str = ""


class SupplyBody(BaseModel):
    kw: float | None = None
    phases: int | None = None
    lat: float | None = None
    lon: float | None = None
    required_element: str | None = None
    text: str = ""


@app.post("/api/whatif")
def whatif_run(body: WhatIfBody):
    return whatif(body.model_dump())


@app.post("/api/runs/{rid}/supply")
def supply_run(rid: str, body: SupplyBody):
    if rid not in RUNS:
        raise HTTPException(404)
    return supply_data(rid, body.model_dump(exclude_none=True))


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


@app.get("/api/runs/{rid}/brief.pdf")
def brief_pdf(rid: str):
    if rid not in RUNS:
        raise HTTPException(404)
    snap = snapshot(RUNS[rid])
    if not (snap.get("escalate") or {}).get("brief"):
        raise HTTPException(404, "Stiprinimo paketo nėra — byla neeskaluota.")
    return Response(brief_pdf_bytes(snap), media_type="application/pdf", headers={"Content-Disposition": f'attachment; filename="{rid}-brief.pdf"'})


dist = ROOT / "web" / "dist"
if dist.exists():
    app.mount("/", StaticFiles(directory=dist, html=True), name="ui")
else:
    demo = ROOT / "demo"

    @app.get("/")
    def fallback():
        html = (demo / "dashboard.html").read_text(encoding="utf-8") if (demo / "dashboard.html").exists() else "<p>Build the web UI: cd web && npm install && npm run build</p>"
        return HTMLResponse(html)

from fastapi.testclient import TestClient

from app.main import app
from eso_agent.document import LAYOUT_BANNER, document_from_snap, render_ts_html
from eso_agent.engine import approve_sync, run_sync_until_interrupt
from eso_agent.fonts import GLYPHS
from eso_agent.pdfutil import render_official_ts_pdf


def test_official_ts_html_and_pdf_two_pages():
    snap = run_sync_until_interrupt("hero", delay=0)
    issued = approve_sync(snap["id"])
    doc = document_from_snap(issued)
    assert str(doc["ts_number"]).startswith("26-E-DEMO-")
    assert doc["voltage_level"] == "0,4 kV"
    assert doc["signature"]["action"] == "approve"
    assert doc["sha256"]
    html = render_ts_html(issued)
    assert LAYOUT_BANNER in html
    assert 'data-page="1"' in html
    assert 'data-page="2"' in html
    assert "Priedas A" in html
    assert "GIS-ANNEX" in html
    assert "TS-PAGE-1" in html
    assert GLYPHS in html
    assert doc["sha256"] in html
    assert "Techniniai parametrai" in html
    assert "0,4 kV" in html
    pdf = render_official_ts_pdf(issued)
    assert pdf[:4] == b"%PDF"
    assert b"DejaVu" in pdf
    assert b"/Count 2" in pdf
    assert b"GIS-ANNEX" in pdf
    assert b"TS-PAGE-1" in pdf
    assert b"26-E-DEMO" in pdf
    raw = pdf.decode("latin-1", errors="ignore")
    assert "SHA-256" in raw or "SHA-256" in html


def test_ts_pdf_endpoint_two_pages():
    with TestClient(app) as c:
        r = c.post("/api/runs", json={"scenario_id": "hero"})
        rid = r.json()["id"]
        for _ in range(80):
            snap = c.get(f"/api/runs/{rid}").json()
            if snap["status"] == "awaiting_approval":
                break
        issued = c.post(f"/api/runs/{rid}/resume", json={"decision": "approve"}).json()
        assert issued["status"] == "issued"
        html = c.get(f"/api/runs/{rid}/ts.html")
        assert html.status_code == 200
        assert 'data-page="2"' in html.text
        assert "Priedas A" in html.text
        assert "ąčęėįšųūž" in html.text
        pdf = c.get(f"/api/runs/{rid}/ts.pdf")
        assert pdf.status_code == 200
        assert pdf.content[:4] == b"%PDF"
        assert b"/Count 2" in pdf.content
        assert b"GIS-ANNEX" in pdf.content
        assert b"DejaVu" in pdf.content

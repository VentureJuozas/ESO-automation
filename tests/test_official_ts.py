from fastapi.testclient import TestClient

from app.main import app
from eso_agent.document import LAYOUT_BANNER, document_from_snap, render_ts_html
from eso_agent.engine import approve_sync, run_sync_until_interrupt
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
    assert "DEMONSTRACINIS" not in html
    assert "n8n" not in html.lower()
    assert LAYOUT_BANNER == ""
    assert "PRIJUNGIMO SĄLYGOS NR." in html
    assert "Nauja leistina naudoti galia" in html
    assert "Kliento prijungimo objekto duomenys" in html
    assert "data:image/jpeg;base64," in html
    assert "Šios prijungimo sąlygos išduodamos" in html
    assert "Elektros tinklų nuosavybės riba nustatyta" in html
    assert "neprašoma" not in html
    assert "Prioritetinė grupė" not in html
    assert "Gamybos tikslas" not in html
    assert "Parkas" not in html
    for glyph in "ąčęėįšųūž":
        assert glyph in html
    assert "200/3" in html
    from io import BytesIO
    from zipfile import ZipFile

    from eso_agent.ts_template import fill_ts_docx

    docx = fill_ts_docx(doc)
    assert docx[:2] == b"PK"
    xml = ZipFile(BytesIO(docx)).read("word/document.xml").decode("utf-8")
    assert doc["ts_number"] in xml
    assert ">11</w:t>" in xml
    assert "trifazis" in xml
    assert "Elektros tinklų nuosavybės riba nustatyta" in xml
    assert "neprašoma" not in xml
    assert "Prioritetinė grupė" not in xml
    assert "Gamybos tikslas" not in xml
    assert ">Parkas<" not in xml
    pdf = render_official_ts_pdf(issued)
    assert pdf[:4] == b"%PDF"
    assert b"DejaVu" in pdf
    assert b"/Count" in pdf


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
        assert "PRIJUNGIMO SĄLYGOS" in html.text
        for glyph in "ąčęėįšųūž":
            assert glyph in html.text
        assert "Nauja leistina naudoti galia" in html.text
        assert "data:image/jpeg;base64," in html.text
        docx = c.get(f"/api/runs/{rid}/ts.docx")
        assert docx.status_code == 200
        assert docx.content[:2] == b"PK"
        pdf = c.get(f"/api/runs/{rid}/ts.pdf")
        assert pdf.status_code == 200
        assert pdf.content[:4] == b"%PDF"
        assert b"DejaVu" in pdf.content

from fastapi.testclient import TestClient

from app.main import app
from eso_agent.engine import approve_sync


def test_portal_submit_track_and_pdf():
    with TestClient(app) as c:
        created = c.post(
            "/api/portal/applications",
            json={"kw": 11, "phases": 3, "lat": 54.55929, "lon": 25.27955, "object_name": "Sodyba (redaguota)"},
        ).json()
        assert created["demo"] is True
        assert "redaguot" in created["address"].lower()
        assert created["status"] in {"tikrinama", "laukia inžinieriaus", "gauta"}
        aid = created["id"]
        got = c.get(f"/api/portal/applications/{aid}").json()
        assert got["customer"].startswith("Buitinis")
        if got["status"] == "laukia inžinieriaus" and got.get("run_id"):
            approve_sync(got["run_id"])
            got = c.get(f"/api/portal/applications/{aid}").json()
            assert got["status"] == "išduota"
            pdf = c.get(f"/api/portal/applications/{aid}/ts.pdf")
            assert pdf.status_code == 200
            assert pdf.content[:4] == b"%PDF"
            assert b"DejaVu" in pdf.content
            html = c.get(f"/api/portal/applications/{aid}/ts.html")
            assert "redaguot" in html.text.lower()
            assert 'data-page="2"' in html.text
            assert "Priedas A" in html.text
            assert b"/Count 2" in pdf.content
            assert b"GIS-ANNEX" in pdf.content
            assert got.get("decision_by")
            assert any(x["status"] == "laukia inžinieriaus" for x in got.get("timeline") or [])


def test_portal_missing_then_answer():
    with TestClient(app) as c:
        created = c.post(
            "/api/portal/applications",
            json={"kw": 11, "phases": 3, "object_name": "Be koordinačių"},
        ).json()
        assert created["status"] == "laukia duomenų"
        assert created["missing"]["letter"]["sent"] is False
        next_ = c.post(
            f"/api/portal/applications/{created['id']}/answer",
            json={"lat": 54.55929, "lon": 25.27955, "kw": 11, "phases": 3},
        ).json()
        assert next_["status"] == "laukia inžinieriaus"


def test_onepager_and_adapters_api():
    with TestClient(app) as c:
        html = c.get("/api/onepager.html")
        assert html.status_code == 200
        assert "95" in html.text
        assert "SHA-256" in html.text
        assert 'translate="no"' in html.text
        ad = c.get("/api/adapters").json()
        assert ad["mode"] == "mock"
        assert len(ad["adapters"]) == 5
        pack = c.get("/api/present").json()
        assert 270000 <= pack["total_ms"] <= 315000
        assert pack["beats"][0]["dwell_ms"] == 20000
        assert any(b["id"] == "split" for b in pack["beats"])
        assert any(b["id"] == "integrations" for b in pack["beats"])
        assert any(b["id"] == "analytics" for b in pack["beats"])
        assert "ąčęėįšųūž" in html.text
        pdf = c.get("/api/onepager.pdf")
        assert pdf.status_code == 200
        assert pdf.content[:4] == b"%PDF"
        assert b"DejaVu" in pdf.content

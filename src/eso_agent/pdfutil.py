"""Unicode PDFs with embedded DejaVu (ąčęėįšųūž)."""
from __future__ import annotations

from typing import Any, Iterable

from fpdf import FPDF

from eso_agent.fonts import DEJAVU, DEJAVU_BOLD, GLYPHS


class _Pdf(FPDF):
    def __init__(self, *, auto_break: bool = True) -> None:
        super().__init__(format="A4")
        self.add_font("DejaVu", "", str(DEJAVU))
        self.add_font("DejaVu", "B", str(DEJAVU_BOLD))
        self.set_auto_page_break(auto=auto_break, margin=18)
        self.add_page()
        self.set_font("DejaVu", size=11)

    def h1(self, text: str) -> None:
        self.set_font("DejaVu", "B", 16)
        self.multi_cell(0, 8, text)
        self.ln(2)
        self.set_font("DejaVu", size=11)

    def h2(self, text: str) -> None:
        self.set_font("DejaVu", "B", 12)
        self.multi_cell(0, 7, text)
        self.ln(1)
        self.set_font("DejaVu", size=11)

    def p(self, text: str) -> None:
        self.multi_cell(0, 6, text)
        self.ln(1)


def _pdf_bytes(pdf: _Pdf) -> bytes:
    return bytes(pdf.output())


def render_ts_pdf(title: str, lines: Iterable[str] | None = None, snap: dict[str, Any] | None = None) -> bytes:
    if snap is not None:
        return render_official_ts_pdf(snap)
    pdf = _Pdf()
    pdf.h1(title)
    pdf.set_font("DejaVu", size=9)
    pdf.p(f"Šriftas DejaVu · lietuviškos raidės: {GLYPHS}")
    pdf.set_font("DejaVu", size=11)
    for line in lines or []:
        pdf.p(str(line))
    return _pdf_bytes(pdf)


def _left(pdf: _Pdf) -> None:
    pdf.set_x(pdf.l_margin)


def _line(pdf: _Pdf, text: str, *, bold: bool = False, size: float = 8, h: float = 4.5) -> None:
    _left(pdf)
    pdf.set_font("DejaVu", "B" if bold else "", size)
    usable = pdf.w - pdf.l_margin - pdf.r_margin
    pdf.multi_cell(usable, h, text)


def _kv(pdf: _Pdf, key: str, value: str) -> None:
    _left(pdf)
    usable = pdf.w - pdf.l_margin - pdf.r_margin
    key_w = 58
    pdf.set_font("DejaVu", "B", 8)
    pdf.cell(key_w, 5, key, border=1)
    pdf.set_font("DejaVu", size=8)
    pdf.cell(usable - key_w, 5, str(value), border=1)
    pdf.ln(5)
    _left(pdf)


def render_official_ts_pdf(snap: dict[str, Any]) -> bytes:
    from eso_agent.document import LAYOUT_BANNER, document_from_snap
    from eso_agent.gis_map import draw_gis_pdf

    doc = document_from_snap(snap)
    pdf = _Pdf(auto_break=False)
    pdf.set_auto_page_break(auto=False)
    number = str(doc.get("ts_number") or "PROJEKTAS")
    pdf.set_title(f"TS {number}")
    pdf.set_keywords(f"TS-PAGE-1 GIS-ANNEX {number}")
    pdf.set_creator("ESO demo layout")
    _left(pdf)
    pdf.set_font("DejaVu", size=7.5)
    pdf.set_fill_color(246, 244, 238)
    usable = pdf.w - pdf.l_margin - pdf.r_margin
    pdf.cell(usable, 5, LAYOUT_BANNER, border=1, align="C", fill=True)
    pdf.ln(7)
    _line(pdf, "AB Energijos skirstymo operatorius · demonstracinis maketas", size=8)
    _line(pdf, "ELEKTROS VARTOTOJO PRIJUNGIMO SĄLYGOS", bold=True, size=13, h=6)
    _line(pdf, "0,4 kV buitinis prijungimas · TP 12-608", size=8)
    pdf.set_font("helvetica", size=7)
    _left(pdf)
    pdf.cell(usable, 4, "TS-PAGE-1")
    pdf.ln(4)
    _line(pdf, f"Registracijos Nr. {number}", bold=True, size=10, h=5)
    _line(pdf, f"Išdavimo data: {doc.get('issue_date') or '—'}   Galioja iki: {doc.get('valid_until') or '—'}")
    if doc.get("watermark"):
        pdf.set_text_color(180, 80, 80)
        _line(pdf, str(doc["watermark"]), bold=True, size=9)
        pdf.set_text_color(17, 17, 17)
    _line(pdf, "Šalys (redaguota)", bold=True, size=9, h=5)
    _kv(pdf, "Klientas", str(doc.get("customer") or ""))
    _kv(pdf, "Identifikatorius", str(doc.get("customer_code") or ""))
    _kv(pdf, "Objektas", str(doc.get("object_name") or ""))
    _kv(pdf, "Objekto vieta", str(doc.get("address") or ""))
    _kv(pdf, "Operatorius", str(doc.get("operator") or ""))
    _line(pdf, "Techniniai parametrai", bold=True, size=9, h=5)
    _kv(pdf, "Leistina naudoti galia", f"{doc.get('kw')} kW")
    _kv(pdf, "Fazės", str(doc.get("phase_label") or ""))
    _kv(pdf, "Automatinis jungiklis", str(doc.get("breaker") or "—"))
    _kv(pdf, "Prijungimo taškas", f"{doc.get('connection_kind')} {doc.get('element')} · {doc.get('feeder')} · TP 12-608")
    _kv(pdf, "Įtampos lygis", str(doc.get("voltage_level") or "0,4 kV"))
    _kv(pdf, "Sprendinio tipas", str(doc.get("solution_label") or doc.get("solution") or "—"))
    _line(pdf, "Sąlygos", bold=True, size=9, h=5)
    _line(pdf, f"1. Nuosavybės riba. {doc.get('section1') or ''}")
    for line in doc.get("section2") or []:
        _line(pdf, str(line))
    s3 = str(doc.get("section3") or "")
    if len(s3) > 620:
        s3 = s3[:620] + " …"
    _line(pdf, "3. Operatoriaus veiksmai. " + s3)
    _line(pdf, "Sąmata ir įsipareigojimai", bold=True, size=9, h=5)
    cost = doc.get("cost") or {}
    for ln in (cost.get("lines") or [])[:5]:
        price = "" if ln.get("price") is None else f"{ln.get('price'):.2f} EUR"
        _line(pdf, f"{ln.get('item')}  {ln.get('qty') or ''} {ln.get('unit') or ''}  {price}")
    if cost.get("gross") is not None:
        _line(pdf, f"Iš viso su PVM: {cost.get('gross'):.2f} EUR   (be PVM {cost.get('net')})", bold=True)
    _line(pdf, str(cost.get("note") or "Orientyras, ne oficiali sąmata."), size=7.5, h=3.5)
    for line in doc.get("obligations") or []:
        _line(pdf, str(line))
    sig = doc.get("signature") or {}
    _line(pdf, "Parašai ir tvirtinimas", bold=True, size=9, h=5)
    y = min(pdf.get_y() + 10, 268)
    pdf.line(12, y, 95, y)
    pdf.line(110, y, 198, y)
    pdf.set_xy(pdf.l_margin, y + 1)
    _line(pdf, f"Parengė: {sig.get('prepared') or ''}")
    _line(pdf, f"Tvirtino: {sig.get('approved') or ''} · {sig.get('action') or ''} · {sig.get('title') or ''} · {sig.get('approved_at') or ''}")
    if sig.get("reason"):
        _line(pdf, str(sig["reason"]))
    pdf.set_xy(pdf.l_margin, 282)
    pdf.set_font("DejaVu", size=7)
    pdf.cell(usable, 4, f"SHA-256 {doc.get('sha256') or '—'}  ·  Puslapis 1 / 2  ·  {GLYPHS}")

    pdf.add_page()
    _left(pdf)
    pdf.set_font("DejaVu", size=7.5)
    pdf.set_fill_color(246, 244, 238)
    pdf.cell(usable, 5, LAYOUT_BANNER, border=1, align="C", fill=True)
    pdf.ln(7)
    _line(pdf, "Priedas A · GIS schema", bold=True, size=13, h=6)
    _line(pdf, "PRIJUNGIMO TAŠKAS, ATRAMA / SPINTA IR LINIJA")
    pdf.set_font("helvetica", size=7)
    _left(pdf)
    pdf.cell(usable, 4, "GIS-ANNEX")
    pdf.ln(4)
    _line(pdf, f"Prie Nr. {number}  ·  {doc.get('connection_kind')} {doc.get('element')}  ·  {doc.get('feeder')}")
    coords = doc.get("coords") or {}
    draw_gis_pdf(pdf, coords.get("lat"), coords.get("lon"), doc.get("element"), doc.get("feeder"))
    pdf.set_xy(pdf.l_margin, 216)
    _line(pdf, "Sutartiniai ženklai ir mastelis", bold=True, size=9, h=5)
    _line(
        pdf,
        "Juodas kvadratas — TP 12-608. Apskritimas — atrama. Kvadratas — spinta. "
        "Raudonas taškas — prijungimo taškas. Punktyras — įvadas. Mastelis ant schemos. "
        f"Lietuviškos raidės: {GLYPHS}. Statinė nuotrauka, piešiama be plytelių serverio.",
    )
    pdf.set_xy(pdf.l_margin, 282)
    pdf.set_font("DejaVu", size=7)
    pdf.cell(usable, 4, f"SHA-256 {doc.get('sha256') or '—'}  ·  Puslapis 2 / 2  ·  GIS-ANNEX  ·  {GLYPHS}")
    return _pdf_bytes(pdf)


def render_brief_pdf(title: str, body_lines: Iterable[str]) -> bytes:
    pdf = _Pdf()
    pdf.h1(title)
    pdf.p(f"Lietuviškos raidės: {GLYPHS}")
    for line in body_lines:
        pdf.p(str(line))
    return _pdf_bytes(pdf)


def render_onepager_pdf() -> bytes:
    pdf = _Pdf()
    pdf.h1("0,4 kV prijungimo sąlygos per minutes, ne dienas")
    pdf.p(
        "Namų ūkiui prie TP 12-608 inžinierius dabar renka GIS, pajėgumą ir šabloną ranka. "
        "Agentas paruošia A/B/C, jungiklį, keturias patikras, §3 ir sąmatą. Sąlygas visada pasirašo žmogus."
    )
    pdf.h2("Kaip veikia")
    pdf.p("1. Klientų maketas pateikia paraišką (redaguota).")
    pdf.p("2. LangGraph eina n8n drobe: parse → locate → A/B/C → patikros.")
    pdf.p("3. Python priima sprendimus. LLM tik skaito tekstą.")
    pdf.p("4. Trūksta duomenų — laiško peržiūra, eiga laukia.")
    pdf.p("5. Inžinierius tvirtina. Auditas + SHA-256.")
    pdf.p("6. Išduotas TS — oficialus maketas ir GIS priedas, 2 puslapiai.")
    pdf.h2("Laikas (prielaida)")
    pdf.p("Rankinis stalas: 2–4 val. paraiškai. Replay: sekundės. 40 bylų / mėn. — ne ESO statistika.")
    pdf.h2("Back-test")
    pdf.p("R3 51 %. R4+ visų 84 %, in-scope 95 %, įrankio klaidų 0. What-if 6/7. Taksonomija a/b/c/d.")
    pdf.h2("Sauga")
    pdf.p("Žmogaus vartai. Override ≥ 8 simboliai. Provenance real/rule/inferred/synthetic. SHA-256. Be vardų.")
    pdf.h2("Toliau — adapteriai")
    pdf.p("GIS, Power BI / SCADA, CRM, kainos, TS registras. Šiandien mock. Stubai dokumentuoti.")
    pdf.h2("Analitika")
    pdf.p("Sintetinis mėnuo SQLite: pralaidumas, medianos, kliūtys, SLA, A/B/C. Valandos — prielaida.")
    pdf.p(f"Šriftas DejaVu. Raidės: {GLYPHS}")
    return _pdf_bytes(pdf)

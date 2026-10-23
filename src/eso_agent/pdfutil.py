"""Unicode PDFs with embedded DejaVu (ąčęėįšųūž)."""
from __future__ import annotations

from typing import Iterable

from fpdf import FPDF

from eso_agent.fonts import DEJAVU, DEJAVU_BOLD, GLYPHS


class _Pdf(FPDF):
    def __init__(self) -> None:
        super().__init__(format="A4")
        self.add_font("DejaVu", "", str(DEJAVU))
        self.add_font("DejaVu", "B", str(DEJAVU_BOLD))
        self.set_auto_page_break(auto=True, margin=18)
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


def render_ts_pdf(title: str, lines: Iterable[str]) -> bytes:
    pdf = _Pdf()
    pdf.h1(title)
    pdf.set_font("DejaVu", size=9)
    pdf.p(f"Šriftas DejaVu · lietuviškos raidės: {GLYPHS}")
    pdf.set_font("DejaVu", size=11)
    for line in lines:
        pdf.p(str(line))
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
    pdf.h2("Laikas (prielaida)")
    pdf.p("Rankinis stalas: 2–4 val. paraiškai. Replay: sekundės. 40 bylų / mėn. — ne ESO statistika.")
    pdf.h2("Back-test")
    pdf.p("R3 51 %. R4+ visų 84 %, in-scope 95 %, įrankio klaidų 0. What-if 6/7. Taksonomija a/b/c/d.")
    pdf.h2("Sauga")
    pdf.p("Žmogaus vartai. Override ≥ 8 simboliai. Provenance real/rule/inferred/synthetic. SHA-256. Be vardų.")
    pdf.h2("Toliau — adapteriai")
    pdf.p("GIS, Power BI / SCADA, CRM, kainos, TS registras. Šiandien mock. Stubai dokumentuoti.")
    pdf.p(f"Šriftas DejaVu. Raidės: {GLYPHS}")
    return _pdf_bytes(pdf)

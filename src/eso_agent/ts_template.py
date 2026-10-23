"""Fill the official TSL2_K1 form and render that same file, logo and wording included."""
from __future__ import annotations

import base64
import re
from html import escape
from io import BytesIO
from pathlib import Path
from typing import Any
from xml.etree import ElementTree as ET
from zipfile import ZIP_DEFLATED, ZipFile

W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
TEMPLATE = Path(__file__).resolve().parents[2] / "data" / "templates" / "TSL2_K1.docx"
_WT = re.compile(r"(<w:t(?:\s[^>]*)?>)([^<]*)(</w:t>)")


def _xml_escape(text: str) -> str:
    return str(text).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def _kw(value: Any) -> str:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return "—"
    if number == int(number):
        return str(int(number))
    return f"{number:.1f}"


def _phase_word(doc: dict[str, Any]) -> str:
    phases = doc.get("phases")
    if phases == 1:
        return "vienfazis"
    if phases == 3:
        return "trifazis"
    label = str(doc.get("phase_label") or "").lower()
    if "vien" in label:
        return "vienfazis"
    if "trif" in label:
        return "trifazis"
    return "—"


def form_values(doc: dict[str, Any]) -> dict[str, str]:
    kw = _kw(doc.get("kw"))
    phase = _phase_word(doc)
    return {
        "prepared": str(doc.get("issue_date") or "—"),
        "number": str(doc.get("ts_number") or "PROJEKTAS"),
        "valid": str(doc.get("valid_until") or "—"),
        "customer": str(doc.get("customer") or "—"),
        "contacts": str(doc.get("customer_code") or "—"),
        "object_name": str(doc.get("object_name") or "—"),
        "address": str(doc.get("address") or "—"),
        "existing_kw": "0",
        "new_kw": kw,
        "total_kw": kw,
        "phase": phase,
        "actions": str(doc.get("section3") or "").replace("\n", " ").strip(),
    }


def _replace_wt(xml: str, prefix: str, new_text: str, *, exact: bool = False) -> str:
    matches = []
    for match in _WT.finditer(xml):
        current = match.group(2)
        hit = current == prefix if exact else current.startswith(prefix)
        if hit:
            matches.append(match)
    if len(matches) != 1:
        raise ValueError(f"{prefix!r} matched {len(matches)} text runs")
    match = matches[0]
    return xml[: match.start(2)] + _xml_escape(new_text) + xml[match.end(2) :]


def _fill_empty_after(xml: str, marker: str, values: list[str]) -> str:
    start = xml.find(marker)
    if start < 0:
        raise ValueError(f"missing template marker {marker!r}")
    pos = start + len(marker)
    for value in values:
        while True:
            opening = xml.find("<w:p ", pos)
            if opening < 0:
                raise ValueError(f"no empty paragraph after {marker!r}")
            closing = xml.find("</w:p>", opening)
            if closing < 0:
                raise ValueError(f"unclosed paragraph after {marker!r}")
            chunk = xml[opening:closing]
            if "<w:t" not in chunk:
                insert = f"<w:r><w:t>{_xml_escape(value)}</w:t></w:r>"
                xml = xml[:closing] + insert + xml[closing:]
                pos = closing + len(insert) + len("</w:p>")
                break
            pos = closing + len("</w:p>")
    return xml


def fill_ts_docx(doc: dict[str, Any]) -> bytes:
    """Copy the TSL2 file and write this case into the empty fields only."""
    values = form_values(doc)
    with ZipFile(TEMPLATE) as source:
        xml = source.read("word/document.xml").decode("utf-8")
        xml = _fill_empty_after(xml, "Esama leistina naudoti galia", [values["existing_kw"]])
        xml = _fill_empty_after(xml, "Nauja leistina naudoti galia", [values["new_kw"], values["phase"]])
        xml = _fill_empty_after(xml, "Visa leistina naudoti galia", [values["total_kw"], values["phase"]])
        xml = _replace_wt(xml, "Parengta:", f"Parengta: {values['prepared']}")
        xml = _replace_wt(xml, "PRIJUNGIMO SĄLYGOS NR.", f"PRIJUNGIMO SĄLYGOS NR. {values['number']}")
        xml = _replace_wt(xml, "Galioja iki:", f"Galioja iki: {values['valid']}")
        xml = _replace_wt(xml, "Klientas:", f"Klientas: {values['customer']}")
        xml = _replace_wt(xml, "Kliento kontaktiniai duomenys:", f"Kliento kontaktiniai duomenys: {values['contacts']}")
        xml = _replace_wt(xml, "Objekto pavadinimas:", f"Objekto pavadinimas: {values['object_name']}")
        xml = _replace_wt(xml, "Objekto adresas:", f"Objekto adresas: {values['address']}")
        if values["actions"]:
            xml = _replace_wt(xml, "Bendroji dalis:", "Bendroji dalis: " + values["actions"], exact=True)
        out = BytesIO()
        with ZipFile(out, "w", compression=ZIP_DEFLATED) as target:
            for info in source.infolist():
                payload = xml.encode("utf-8") if info.filename == "word/document.xml" else source.read(info.filename)
                target.writestr(info, payload)
    return out.getvalue()


def _on(element: ET.Element | None) -> bool:
    if element is None:
        return False
    val = element.get(W + "val")
    return val not in {"0", "false", "off"}


def _run_html(run: ET.Element) -> str:
    chunks: list[str] = []
    if run.find(W + "tab") is not None:
        chunks.append("&emsp;")
    if run.find(W + "br") is not None:
        chunks.append("<br>")
    text = "".join(node.text or "" for node in run.findall(W + "t"))
    if not text:
        return "".join(chunks)
    rpr = run.find(W + "rPr")
    style: list[str] = []
    if rpr is not None and _on(rpr.find(W + "b")):
        style.append("font-weight:700")
    if rpr is not None and _on(rpr.find(W + "i")):
        style.append("font-style:italic")
    if rpr is not None:
        size = rpr.find(W + "sz")
        if size is not None and size.get(W + "val"):
            style.append(f"font-size:{int(size.get(W + 'val')) / 2:g}pt")
        color = rpr.find(W + "color")
        if color is not None and color.get(W + "val") and color.get(W + "val") != "auto":
            style.append(f"color:#{color.get(W + 'val')}")
    span = escape(text)
    if style:
        span = f'<span style="{";".join(style)}">{span}</span>'
    chunks.append(span)
    return "".join(chunks)


def _paragraph_html(paragraph: ET.Element) -> str:
    align = ""
    ppr = paragraph.find(W + "pPr")
    if ppr is not None:
        jc = ppr.find(W + "jc")
        if jc is not None and jc.get(W + "val") in {"right", "center", "both"}:
            value = "justify" if jc.get(W + "val") == "both" else jc.get(W + "val")
            align = f' style="text-align:{value}"'
    inner = "".join(_run_html(run) for run in paragraph.iter(W + "r"))
    if not inner.strip():
        inner = "&nbsp;"
    return f"<p{align}>{inner}</p>"


def _table_html(table: ET.Element) -> str:
    rows: list[str] = []
    for row in table.findall(W + "tr"):
        cells: list[str] = []
        for cell in row.findall(W + "tc"):
            span = ""
            tcpr = cell.find(W + "tcPr")
            if tcpr is not None:
                grid = tcpr.find(W + "gridSpan")
                if grid is not None and grid.get(W + "val") not in {None, "1"}:
                    span = f' colspan="{grid.get(W + "val")}"'
            inner = "".join(_paragraph_html(p) for p in cell.findall(W + "p"))
            cells.append(f"<td{span}>{inner}</td>")
        rows.append("<tr>" + "".join(cells) + "</tr>")
    return '<table>' + "".join(rows) + "</table>"


def _part_html(root: ET.Element) -> str:
    body = root.find(W + "body")
    parent = body if body is not None else root
    chunks: list[str] = []
    for child in list(parent):
        name = child.tag.split("}")[-1]
        if name == "p":
            chunks.append(_paragraph_html(child))
        elif name == "tbl":
            chunks.append(_table_html(child))
    return "".join(chunks)


def _logo_src(source: ZipFile) -> str:
    raw = source.read("word/media/image1.jpg")
    return "data:image/jpeg;base64," + base64.b64encode(raw).decode("ascii")


def _footer_html(source: ZipFile) -> str:
    seen: list[str] = []
    for name in source.namelist():
        if not name.startswith("word/footer"):
            continue
        html = _part_html(ET.fromstring(source.read(name)))
        if html and html not in seen:
            seen.append(html)
    return "".join(seen)


def plain_blocks(docx_bytes: bytes) -> tuple[list[str], bytes]:
    """Template text in reading order, plus the header logo."""
    lines: list[str] = []
    with ZipFile(BytesIO(docx_bytes)) as source:
        root = ET.fromstring(source.read("word/document.xml"))
        body = root.find(W + "body")
        for child in list(body):
            name = child.tag.split("}")[-1]
            if name == "p":
                text = "".join(node.text or "" for node in child.iter(W + "t")).strip()
                if text:
                    lines.append(text)
            elif name == "tbl":
                for row in child.findall(W + "tr"):
                    cells = [
                        " ".join(node.text or "" for node in cell.iter(W + "t")).strip()
                        for cell in row.findall(W + "tc")
                    ]
                    cells = [cell for cell in cells if cell]
                    if cells:
                        lines.append("  |  ".join(cells))
        for name in source.namelist():
            if not name.startswith("word/footer"):
                continue
            root = ET.fromstring(source.read(name))
            text = "".join(node.text or "" for node in root.iter(W + "t")).strip()
            if text and text not in lines:
                lines.append(text)
        logo = source.read("word/media/image1.jpg")
    return lines, logo


def render_docx_html(docx_bytes: bytes, *, run_id: str = "") -> str:
    """HTML of the filled Word file: same logo, table, and sentences."""
    with ZipFile(BytesIO(docx_bytes)) as source:
        body = _part_html(ET.fromstring(source.read("word/document.xml")))
        footer = _footer_html(source)
        logo = _logo_src(source)
    word = f'<a href="/api/runs/{escape(run_id)}/ts.docx">Word</a>' if run_id else ""
    pdf = f'<a href="/api/runs/{escape(run_id)}/ts.pdf">PDF</a>' if run_id else ""
    return f"""<!DOCTYPE html>
<html lang="lt">
<head>
<meta charset="utf-8">
<title>PRIJUNGIMO SĄLYGOS</title>
<style>
  @page {{ size: A4; margin: 16mm 11mm 18mm 20mm; }}
  html, body {{ margin: 0; background: #d9d9d9; }}
  body {{ font-family: Calibri, "Segoe UI", Arial, sans-serif; color: #000; }}
  .tools {{ width: 210mm; margin: 10px auto; font-family: Calibri, Arial, sans-serif; font-size: 12px; }}
  .tools a, .tools button {{
    margin-right: 8px; color: #000; background: #fff; border: 1px solid #000;
    padding: 4px 8px; text-decoration: none; font: inherit; cursor: pointer;
  }}
  .sheet {{
    width: 210mm; min-height: 297mm; margin: 0 auto 16px; background: #fff;
    box-sizing: border-box; padding: 14mm 11mm 16mm 20mm;
  }}
  .logo {{ width: 71mm; height: auto; display: block; margin: 0 0 8mm; }}
  p {{ margin: 0 0 8pt; font-size: 12pt; line-height: 1.15; }}
  table {{ width: 100%; border-collapse: collapse; margin: 6pt 0 10pt; }}
  td {{ border: 1px solid #000; padding: 1px 4px; vertical-align: top; }}
  td p {{ margin: 0; font-size: 11pt; }}
  .foot {{ margin-top: 12pt; }}
  .foot p {{ font-size: 8pt; line-height: 1.2; margin: 0 0 2pt; }}
  @media print {{
    html, body {{ background: #fff; }}
    .tools {{ display: none; }}
    .sheet {{ margin: 0; width: auto; min-height: auto; padding: 0; }}
  }}
</style>
</head>
<body>
<div class="tools"><button onclick="window.print()">Spausdinti</button>{word}{pdf}</div>
<article class="sheet">
<img class="logo" src="{logo}" alt="ESO">
{body}
<div class="foot">{footer}</div>
</article>
</body>
</html>"""

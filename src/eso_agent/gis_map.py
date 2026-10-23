"""Offline GIS annex: static map of the connection point, pole/cabinet and line."""
from __future__ import annotations

from html import escape
from typing import Any

from eso_agent.network import STATION, haversine_m, load_network

KIND_LT = {"pole": "Atrama", "cabinet": "Spinta"}
FEEDER_COLORS = {
    "L-200": "#1e88e5",
    "L-204": "#7c4dff",
    "L-300": "#00a99d",
    "L-KS14330": "#e5484d",
    "L-KS39685": "#fb8c00",
    "L-KS13058": "#2e9e5b",
}


def _project(lat: float, lon: float, bounds: tuple[float, float, float, float], w: float, h: float, pad: float):
    min_lat, max_lat, min_lon, max_lon = bounds
    lat_span = max(max_lat - min_lat, 1e-6)
    lon_span = max(max_lon - min_lon, 1e-6)
    x = pad + (lon - min_lon) / lon_span * (w - 2 * pad)
    y = pad + (max_lat - lat) / lat_span * (h - 2 * pad)
    return x, y


def scene(lat: float | None, lon: float | None, element_id: str | None, feeder: str | None, *, w: float = 640.0, h: float = 420.0) -> dict[str, Any]:
    net = load_network()
    station = net["substation"]
    els = list(net["elements"])
    focus = [e for e in els if feeder and e.get("feeder") == feeder]
    if not focus:
        focus = els[:24]
    extras = [e for e in els if e.get("id") == element_id]
    pts = [(station["lat"], station["lon"])]
    if lat and lon:
        pts.append((float(lat), float(lon)))
    for e in focus + extras:
        pts.append((e["lat"], e["lon"]))
    lats = [p[0] for p in pts]
    lons = [p[1] for p in pts]
    pad_deg = 0.00035
    bounds = (min(lats) - pad_deg, max(lats) + pad_deg, min(lons) - pad_deg, max(lons) + pad_deg)
    mid_lat = (bounds[0] + bounds[1]) / 2
    m_per_lon = 111320.0 * max(0.3, abs(__import__("math").cos(__import__("math").radians(mid_lat))))
    m_per_lat = 111320.0
    span_m = max((bounds[1] - bounds[0]) * m_per_lat, (bounds[3] - bounds[2]) * m_per_lon, 40.0)
    px_per_m = (w - 48) / span_m

    def xy(la: float, lo: float) -> tuple[float, float]:
        return _project(la, lo, bounds, w, h, 28.0)

    lines = []
    by_feeder: dict[str, list[dict[str, Any]]] = {}
    for e in focus:
        by_feeder.setdefault(e["feeder"], []).append(e)
    sx, sy = xy(station["lat"], station["lon"])
    for name, group in by_feeder.items():
        group = sorted(group, key=lambda e: haversine_m(station["lat"], station["lon"], e["lat"], e["lon"]))
        prev = (sx, sy)
        color = FEEDER_COLORS.get(name, "#555")
        for e in group:
            x, y = xy(e["lat"], e["lon"])
            lines.append({"x1": prev[0], "y1": prev[1], "x2": x, "y2": y, "color": color, "kind": "feeder", "name": name})
            prev = (x, y)

    items = []
    for e in focus:
        x, y = xy(e["lat"], e["lon"])
        items.append(
            {
                "id": e["id"],
                "kind": e.get("kind") or "pole",
                "x": x,
                "y": y,
                "highlight": e["id"] == element_id,
                "feeder": e.get("feeder"),
                "color": FEEDER_COLORS.get(e.get("feeder") or "", "#333"),
            }
        )

    req = xy(float(lat), float(lon)) if lat and lon else None
    sel = next((i for i in items if i["highlight"]), None)
    service = None
    if req and sel:
        service = {"x1": req[0], "y1": req[1], "x2": sel["x"], "y2": sel["y"]}

    return {
        "w": w,
        "h": h,
        "station": {"x": sx, "y": sy, "id": station["id"]},
        "items": items,
        "lines": lines,
        "request": {"x": req[0], "y": req[1]} if req else None,
        "service": service,
        "px_per_m": px_per_m,
        "scale_m": 50 if span_m < 220 else 100,
        "element_id": element_id,
        "feeder": feeder,
        "lat": lat,
        "lon": lon,
        "kind_lt": KIND_LT.get((sel or {}).get("kind") or "pole", "Elementas"),
    }


def render_gis_svg(lat: float | None, lon: float | None, element_id: str | None, feeder: str | None) -> str:
    sc = scene(lat, lon, element_id, feeder)
    w, h = sc["w"], sc["h"]
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w:.0f} {h:.0f}" width="100%" role="img" aria-label="GIS priedas">',
        f'<rect width="{w:.0f}" height="{h:.0f}" fill="#f4f1ea"/>',
        '<rect x="8" y="8" width="{:.0f}" height="{:.0f}" fill="none" stroke="#1c1c1f" stroke-width="1.2"/>'.format(w - 16, h - 16),
    ]
    for ln in sc["lines"]:
        parts.append(
            f'<line x1="{ln["x1"]:.1f}" y1="{ln["y1"]:.1f}" x2="{ln["x2"]:.1f}" y2="{ln["y2"]:.1f}" '
            f'stroke="{ln["color"]}" stroke-width="2.2" stroke-linecap="round"/>'
        )
    if sc.get("service"):
        s = sc["service"]
        parts.append(
            f'<line x1="{s["x1"]:.1f}" y1="{s["y1"]:.1f}" x2="{s["x2"]:.1f}" y2="{s["y2"]:.1f}" '
            f'stroke="#111" stroke-width="1.6" stroke-dasharray="5 3"/>'
        )
    st = sc["station"]
    parts.append(f'<rect x="{st["x"]-8:.1f}" y="{st["y"]-8:.1f}" width="16" height="16" fill="#111"/>')
    parts.append(f'<text x="{st["x"]+12:.1f}" y="{st["y"]+4:.1f}" font-size="11" font-family="DejaVu, sans-serif">TP {escape(st["id"])}</text>')
    for it in sc["items"]:
        if it["kind"] == "cabinet":
            parts.append(
                f'<rect x="{it["x"]-5:.1f}" y="{it["y"]-5:.1f}" width="10" height="10" fill="#fff" '
                f'stroke="{it["color"]}" stroke-width="{3 if it["highlight"] else 1.5}"/>'
            )
        else:
            parts.append(
                f'<circle cx="{it["x"]:.1f}" cy="{it["y"]:.1f}" r="{6 if it["highlight"] else 4}" fill="#fff" '
                f'stroke="{it["color"]}" stroke-width="{3 if it["highlight"] else 1.5}"/>'
            )
        if it["highlight"]:
            parts.append(
                f'<text x="{it["x"]+9:.1f}" y="{it["y"]-8:.1f}" font-size="11" font-weight="700" '
                f'font-family="DejaVu, sans-serif">{escape(it["id"])}</text>'
            )
    if sc.get("request"):
        r = sc["request"]
        parts.append(
            f'<path d="M{r["x"]:.1f} {r["y"]-8:.1f} L{r["x"]+6:.1f} {r["y"]+6:.1f} L{r["x"]-6:.1f} {r["y"]+6:.1f} Z" fill="#e11d48"/>'
        )
        parts.append(
            f'<text x="{r["x"]+10:.1f}" y="{r["y"]+14:.1f}" font-size="11" font-family="DejaVu, sans-serif">Prijungimo taškas</text>'
        )
    bar = sc["scale_m"] * sc["px_per_m"]
    bx, by = 28, h - 28
    parts.append(f'<line x1="{bx:.1f}" y1="{by:.1f}" x2="{bx+bar:.1f}" y2="{by:.1f}" stroke="#111" stroke-width="2"/>')
    parts.append(f'<line x1="{bx:.1f}" y1="{by-4:.1f}" x2="{bx:.1f}" y2="{by+4:.1f}" stroke="#111" stroke-width="2"/>')
    parts.append(f'<line x1="{bx+bar:.1f}" y1="{by-4:.1f}" x2="{bx+bar:.1f}" y2="{by+4:.1f}" stroke="#111" stroke-width="2"/>')
    parts.append(
        f'<text x="{bx:.1f}" y="{by-8:.1f}" font-size="10" font-family="DejaVu, sans-serif">{sc["scale_m"]} m</text>'
    )
    parts.append("</svg>")
    return "".join(parts)


def draw_gis_pdf(pdf: Any, lat: float | None, lon: float | None, element_id: str | None, feeder: str | None) -> None:
    """Draw the annex map into the current fpdf page (mm)."""
    x0, y0, mw, mh = 12.0, 42.0, 186.0, 168.0
    sc = scene(lat, lon, element_id, feeder, w=mw, h=mh)
    pdf.set_fill_color(244, 241, 234)
    pdf.rect(x0, y0, mw, mh, "F")
    pdf.set_draw_color(28, 28, 31)
    pdf.set_line_width(0.3)
    pdf.rect(x0, y0, mw, mh, "D")

    def abs_xy(x: float, y: float) -> tuple[float, float]:
        return x0 + x, y0 + y

    def hex_rgb(color: str) -> tuple[int, int, int]:
        c = color.lstrip("#")
        return int(c[0:2], 16), int(c[2:4], 16), int(c[4:6], 16)

    for ln in sc["lines"]:
        r, g, b = hex_rgb(ln["color"])
        pdf.set_draw_color(r, g, b)
        pdf.set_line_width(0.7)
        x1, y1 = abs_xy(ln["x1"], ln["y1"])
        x2, y2 = abs_xy(ln["x2"], ln["y2"])
        pdf.line(x1, y1, x2, y2)
    if sc.get("service"):
        s = sc["service"]
        pdf.set_draw_color(17, 17, 17)
        pdf.set_line_width(0.4)
        pdf.line(*abs_xy(s["x1"], s["y1"]), *abs_xy(s["x2"], s["y2"]))
    st = sc["station"]
    sx, sy = abs_xy(st["x"], st["y"])
    pdf.set_fill_color(17, 17, 17)
    pdf.rect(sx - 2.2, sy - 2.2, 4.4, 4.4, "F")
    pdf.set_text_color(17, 17, 17)
    pdf.set_font("DejaVu", size=8)
    pdf.set_xy(sx + 3.2, sy - 2.4)
    pdf.cell(30, 5, f"TP {st['id']}")
    for it in sc["items"]:
        ix, iy = abs_xy(it["x"], it["y"])
        r, g, b = hex_rgb(it["color"])
        pdf.set_draw_color(r, g, b)
        pdf.set_fill_color(255, 255, 255)
        pdf.set_line_width(0.9 if it["highlight"] else 0.4)
        if it["kind"] == "cabinet":
            pdf.rect(ix - 1.6, iy - 1.6, 3.2, 3.2, "FD")
        else:
            pdf.ellipse(ix - 1.5, iy - 1.5, 3.0, 3.0, "FD")
        if it["highlight"]:
            pdf.set_font("DejaVu", "B", 8)
            pdf.set_xy(ix + 2.4, iy - 4.2)
            pdf.cell(28, 4, it["id"])
    if sc.get("request"):
        r = sc["request"]
        rx, ry = abs_xy(r["x"], r["y"])
        pdf.set_fill_color(225, 29, 72)
        pdf.ellipse(rx - 1.8, ry - 1.8, 3.6, 3.6, "F")
        pdf.set_font("DejaVu", size=8)
        pdf.set_xy(rx + 3, ry + 1)
        pdf.cell(40, 4, "Prijungimo taškas")
    bar = sc["scale_m"] * sc["px_per_m"]
    bx, by = abs_xy(18, mh - 14)
    pdf.set_draw_color(17, 17, 17)
    pdf.set_line_width(0.5)
    pdf.line(bx, by, bx + bar, by)
    pdf.line(bx, by - 1.4, bx, by + 1.4)
    pdf.line(bx + bar, by - 1.4, bx + bar, by + 1.4)
    pdf.set_font("DejaVu", size=8)
    pdf.set_xy(bx, by - 5)
    pdf.cell(24, 4, f"{sc['scale_m']} m")
    pdf.set_text_color(17, 17, 17)

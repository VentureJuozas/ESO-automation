import { useEffect, useRef } from "react";
import L from "leaflet";
import "leaflet/dist/leaflet.css";
import { fmtLt } from "../steps.js";
import SourceTags from "./SourceTags.jsx";

function paper(m, label) {
  const pane = m.getPane("tilePane");
  if (pane) pane.style.background = "#d5e0c6";
  m.attributionControl?.setPrefix("");
  m.attributionControl?.addAttribution(label || "Offline schema · be plytelių");
}

function addTiles(m) {
  const offline = document.body?.dataset?.offline === "1" || /offline=1/.test(window.location.search);
  if (offline) {
    paper(m, "Šaldytas replay · schema be tinklo");
    return;
  }
  const esri = L.tileLayer("https://server.arcgisonline.com/ArcGIS/rest/services/World_Street_Map/MapServer/tile/{z}/{y}/{x}", {
    maxZoom: 19,
    attribution: "Tiles © Esri · topologija sintetinė",
  });
  const osm = L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
    maxZoom: 19,
    attribution: "© OpenStreetMap · topologija sintetinė",
  });
  esri.addTo(m);
  let swapped = false;
  esri.on("tileerror", () => {
    if (swapped) return;
    swapped = true;
    m.removeLayer(esri);
    osm.addTo(m);
    let papered = false;
    osm.on("tileerror", () => {
      if (papered) return;
      papered = true;
      m.removeLayer(osm);
      paper(m);
    });
  });
}

function drawMap(el, map, pickable, onPick) {
  if (!el) return null;
  const m = L.map(el, { zoomControl: true, attributionControl: true, scrollWheelZoom: !pickable });
  addTiles(m);
  const colors = Object.fromEntries((map.feeders || []).map((f) => [f.name, f.color]));
  const bounds = [];
  const sub = map.substation;
  if (sub) {
    L.circleMarker([sub.lat, sub.lon], {
      radius: 13, color: "#111", weight: 3, fillColor: "#ffd166", fillOpacity: 1,
    }).addTo(m).bindPopup(`<b>TP ${sub.id || "12-608"}</b><br>400 kW · 227,7 kW viršūnė`);
    L.marker([sub.lat, sub.lon], {
      icon: L.divIcon({ className: "map-label strong", html: "TP 12-608", iconSize: [78, 18], iconAnchor: [-10, 10] }),
      interactive: false,
    }).addTo(m);
    bounds.push([sub.lat, sub.lon]);
  }
  const line = map.line?.path || [];
  if (line.length > 1) {
    L.polyline(line, { color: "#3b1d8f", weight: 5, opacity: 0.95 }).addTo(m);
  }
  (map.elements || []).forEach((pt) => {
    const selected = pt.id === map.selected?.id;
    L.circleMarker([pt.lat, pt.lon], {
      radius: selected ? 10 : 6,
      color: "#111",
      weight: selected ? 3 : 2,
      fillColor: selected ? "#ff3b2e" : (colors[pt.feeder] || "#222"),
      fillOpacity: 1,
    }).addTo(m).bindPopup(`${pt.feeder} · ${pt.kind === "pole" ? "atrama" : "spinta"} ${pt.id}`);
    bounds.push([pt.lat, pt.lon]);
  });
  if (map.request) {
    L.circleMarker([map.request.lat, map.request.lon], {
      radius: 10, color: "#111", weight: 3, fillColor: "#ffe08a", fillOpacity: 1,
    }).addTo(m).bindPopup("Paraiškos taškas (be adreso)");
    bounds.push([map.request.lat, map.request.lon]);
    if (map.selected) {
      L.polyline(
        [[map.request.lat, map.request.lon], [map.selected.lat, map.selected.lon]],
        { color: "#111", weight: 3, dashArray: "5 5" },
      ).addTo(m);
    }
  }
  if (pickable && onPick) {
    m.on("click", (ev) => onPick({ lat: Number(ev.latlng.lat.toFixed(5)), lon: Number(ev.latlng.lng.toFixed(5)) }));
  }
  if (bounds.length) m.fitBounds(bounds, { padding: [28, 28] });
  else if (map.request) m.setView([map.request.lat, map.request.lon], 17);
  setTimeout(() => m.invalidateSize(), 80);
  return m;
}

export default function MapPanel({ map, pickable = false, onPick }) {
  const ref = useRef(null);
  const inst = useRef(null);
  useEffect(() => {
    if (!ref.current || !map) return undefined;
    if (inst.current) {
      inst.current.remove();
      inst.current = null;
    }
    inst.current = drawMap(ref.current, map, pickable, onPick);
    return () => {
      inst.current?.remove();
      inst.current = null;
    };
  }, [map, pickable, onPick]);
  if (!map) return <div className="empty">Žemėlapis atsiras paleidus eigą arba pasirinkus tašką.</div>;
  const sel = map.selected;
  return (
    <div className="section">
      <h3>Tinklo taškas · L linija · TP 12-608</h3>
      <div className={`map${pickable ? " pickable" : ""}`} ref={ref} />
      <div className="kv" style={{ marginTop: 10 }}>
        <div><b>Paraiška</b><span>{map.request ? `${map.request.lat}, ${map.request.lon}` : "—"}</span></div>
        <div><b>Artimiausia</b><span>{sel ? `${sel.kind === "pole" ? "atrama" : "spinta"} ${sel.id}` : "—"}</span></div>
        <div><b>Atstumas</b><span>{map.distance_m != null ? `${fmtLt(map.distance_m, 1)} m` : "—"}</span></div>
        <div><b>Linija</b><span>{map.line?.name || sel?.feeder || "—"}</span></div>
      </div>
      {pickable && <p className="hint" style={{ marginTop: 10 }}>Spustelėkite žemėlapį — paraiškos taškas persikels.</p>}
      <p className="map-note">Atramos ir L-200 geometrija sintetinė. Be klientų adresų. Esri plytelės, gedus — OSM. <SourceTags tags={["synthetic", "real"]} /></p>
    </div>
  );
}

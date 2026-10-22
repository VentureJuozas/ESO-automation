import { useEffect, useRef } from "react";
import L from "leaflet";
import "leaflet/dist/leaflet.css";
import { fmtLt } from "../steps.js";
import SourceTags from "./SourceTags.jsx";

function drawMap(el, map, pickable, onPick) {
  const m = L.map(el, { zoomControl: true, attributionControl: true, scrollWheelZoom: true });
  L.tileLayer("https://server.arcgisonline.com/ArcGIS/rest/services/World_Street_Map/MapServer/tile/{z}/{y}/{x}", {
    maxZoom: 19,
    attribution: "Tiles © Esri · topologija sintetinė",
  }).addTo(m);
  const colors = Object.fromEntries((map.feeders || []).map((f) => [f.name, f.color]));
  const bounds = [];
  const sub = map.substation;
  if (sub) {
    L.circleMarker([sub.lat, sub.lon], {
      radius: 10, color: "#fff", weight: 2, fillColor: "#1c1c1f", fillOpacity: 1,
    }).addTo(m).bindPopup(`<b>TP ${sub.id || "12-608"}</b><br>400 kW · 227,7 kW viršūnė`);
    L.marker([sub.lat, sub.lon], {
      icon: L.divIcon({ className: "map-label", html: "TP 12-608", iconSize: [72, 16], iconAnchor: [-8, 8] }),
      interactive: false,
    }).addTo(m);
    bounds.push([sub.lat, sub.lon]);
  }
  const line = map.line?.path || [];
  if (line.length > 1) {
    L.polyline(line, { color: "#7c5cfc", weight: 4, opacity: 0.85 }).addTo(m);
  }
  (map.elements || []).forEach((pt) => {
    const selected = pt.id === map.selected?.id;
    L.circleMarker([pt.lat, pt.lon], {
      radius: selected ? 8 : 4,
      color: "#fff",
      weight: selected ? 2 : 1,
      fillColor: selected ? "#ff6d5a" : (colors[pt.feeder] || "#888"),
      fillOpacity: 0.95,
    }).addTo(m).bindPopup(`${pt.feeder} · ${pt.kind === "pole" ? "atrama" : "spinta"} ${pt.id}`);
    bounds.push([pt.lat, pt.lon]);
  });
  if (map.request) {
    L.circleMarker([map.request.lat, map.request.lon], {
      radius: 8, color: "#ffd166", weight: 3, fillColor: "#1c1c1f", fillOpacity: 1,
    }).addTo(m).bindPopup("Paraiškos taškas (be adreso)");
    bounds.push([map.request.lat, map.request.lon]);
    if (map.selected) {
      L.polyline(
        [[map.request.lat, map.request.lon], [map.selected.lat, map.selected.lon]],
        { color: "#1c1c1f", weight: 2, dashArray: "5 5" },
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
      <p className="map-note">Atramos ir L-200 geometrija sintetinė. Be klientų adresų. <SourceTags tags={["synthetic", "real"]} /></p>
    </div>
  );
}

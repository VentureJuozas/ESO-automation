import { useEffect, useRef } from "react";
import L from "leaflet";
import "leaflet/dist/leaflet.css";

export default function MapPanel({ map }) {
  const ref = useRef(null);
  const inst = useRef(null);
  useEffect(() => {
    if (!ref.current || !map) return;
    if (inst.current) {
      inst.current.remove();
      inst.current = null;
    }
    const sub = map.substation;
    const m = L.map(ref.current, { zoomControl: true, attributionControl: true });
    inst.current = m;
    L.tileLayer("https://server.arcgisonline.com/ArcGIS/rest/services/World_Street_Map/MapServer/tile/{z}/{y}/{x}", {
      maxZoom: 19,
      attribution: "Tiles © Esri",
    }).addTo(m);
    const colors = Object.fromEntries((map.feeders || []).map((f) => [f.name, f.color]));
    const bounds = [];
    L.circleMarker([sub.lat, sub.lon], { radius: 8, color: "#fff", weight: 2, fillColor: "#1c1c1f", fillOpacity: 1 })
      .addTo(m)
      .bindPopup("TP 12-608");
    bounds.push([sub.lat, sub.lon]);
    (map.elements || []).forEach((el) => {
      const mk = L.circleMarker([el.lat, el.lon], {
        radius: el.id === map.selected?.id ? 8 : 4,
        color: "#fff",
        weight: 1,
        fillColor: colors[el.feeder] || "#888",
        fillOpacity: 0.9,
      }).addTo(m);
      mk.bindPopup(`${el.feeder} · ${el.kind} ${el.id}`);
      bounds.push([el.lat, el.lon]);
    });
    if (map.request) {
      L.circleMarker([map.request.lat, map.request.lon], {
        radius: 7, color: "#ffd166", weight: 3, fillColor: "#1c1c1f", fillOpacity: 1,
      }).addTo(m).bindPopup("Paraiška");
      bounds.push([map.request.lat, map.request.lon]);
    }
    if (bounds.length) m.fitBounds(bounds, { padding: [24, 24] });
    setTimeout(() => m.invalidateSize(), 80);
    return () => {
      m.remove();
      inst.current = null;
    };
  }, [map]);
  if (!map) return <div className="empty">Žemėlapis atsiras paleidus eigą.</div>;
  return (
    <div className="section">
      <h3>Prijungimo taškas</h3>
      <div className="map" ref={ref} />
      <p style={{ color: "var(--muted)", fontSize: 12, marginTop: 8 }}>
        Parinkta: {map.selected?.kind} {map.selected?.id} · {map.solution}. Atramos/spintos sintetinės; be klientų adresų.
      </p>
    </div>
  );
}

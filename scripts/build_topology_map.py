"""Build demo/topology_map.html: the 12-608 connection points on an OpenStreetMap.

Reads data/substation_12-608/raw/ (git-ignored). The output embeds customer coordinates, so demo/ is
git-ignored too. No names, addresses or meter serials are written into the map.
"""
import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "substation_12-608" / "raw"
OUT = ROOT / "demo" / "topology_map.html"

sub = next(csv.DictReader(open(RAW / "Substations_info.csv", encoding="utf-8-sig")))
points = []
for r in csv.DictReader(open(RAW / "Objects_network_power.csv", encoding="utf-8-sig")):
    points.append({
        "feeder": r["feeder_04kv_oper_name"],
        "kind": "pole" if r["pole"] != "NULL" else "cabinet",
        "where": r["pole"] if r["pole"] != "NULL" else r["cable_cabinet"],
        "phases": r["meter_phase_count"],
        "kw": float(r["permitted_power"]),
        "lon": float(r["object_x_wgs"]),
        "lat": float(r["object_y_wgs"]),
    })

data = {
    "substation": {
        "name": sub["substation_name"],
        "lon": float(sub["PAS_X_WGS"]),
        "lat": float(sub["PAS_Y_WGS"]),
        "kw": float(sub["nominal_power_kW"]),
    },
    "points": points,
}

TEMPLATE = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>12-608 topology on the map</title>
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css">
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<style>
  * { box-sizing: border-box; }
  body { margin: 0; font-family: "Segoe UI", system-ui, sans-serif; color: #14213d; }
  #map { position: absolute; inset: 0; }
  .panel { position: absolute; z-index: 500; background: #fff; border-radius: 10px;
           box-shadow: 0 2px 10px rgba(20,33,61,.25); }
  .legend { top: 14px; left: 14px; padding: 12px 14px; width: 230px; }
  .legend h1 { font-size: 15px; margin: 0 0 2px; }
  .legend .sub { font-size: 12px; color: #5b6b86; margin: 0 0 8px; }
  .legend label { display: flex; align-items: center; gap: 8px; font-size: 13px; margin: 3px 0; cursor: pointer; }
  .sw { width: 12px; height: 12px; border-radius: 50%; display: inline-block; }
  .result { top: 14px; right: 14px; width: 320px; padding: 14px; display: none; }
  .result h2 { font-size: 14px; margin: 0 0 6px; }
  .result p { font-size: 13px; margin: 4px 0; }
  .muted { color: #5b6b86; }
  .pill { display: inline-block; color: #fff; border-radius: 999px; padding: 2px 10px; font-weight: 700; font-size: 12px; }
  .note { position: absolute; z-index: 500; bottom: 14px; left: 50%; transform: translateX(-50%);
          background: #14213d; color: #fff; border-radius: 999px; padding: 7px 16px; font-size: 13px; }
</style>
</head>
<body>
<div id="map"></div>
<div class="panel legend">
  <h1>Substation 12-608</h1>
  <p class="sub">221 connection points, coloured by 0.4 kV feeder. Click the map to place a new request.</p>
  <div id="legend"></div>
</div>
<div class="panel result" id="result"></div>
<div class="note" id="note">Step 1: the request is a coordinate. Click the map to drop it on the topology.</div>
<script>
const DATA = __DATA__;
const COLORS = {
  "L-200": "#1e88e5", "L-204": "#7c4dff", "L-300": "#00a99d",
  "L-KS14330": "#e5484d", "L-KS39685": "#fb8c00", "L-KS13058": "#2e9e5b",
};
const map = L.map("map");
L.tileLayer("https://server.arcgisonline.com/ArcGIS/rest/services/World_Street_Map/MapServer/tile/{z}/{y}/{x}", {
  maxZoom: 19,
  attribution: "Tiles &copy; Esri",
}).addTo(map);

const sub = DATA.substation;
L.marker([sub.lat, sub.lon], {
  icon: L.divIcon({ className: "", html: '<div style="background:#14213d;color:#fff;border-radius:4px;padding:2px 6px;font:700 12px Segoe UI;white-space:nowrap;transform:translate(-50%,-130%)">TP 12-608</div><div style="width:14px;height:14px;background:#14213d;border:2px solid #fff;border-radius:50%;transform:translate(-2px,-6px)"></div>', iconSize: [14, 14] }),
}).addTo(map).bindPopup("<b>Transformer station 12-608</b><br>1 transformer, " + sub.kw + " kW nominal");

const groups = {};
Object.keys(COLORS).forEach(f => groups[f] = L.layerGroup().addTo(map));
const bounds = [];
DATA.points.forEach(p => {
  const m = L.circleMarker([p.lat, p.lon], {
    radius: 5, color: "#fff", weight: 1, fillColor: COLORS[p.feeder], fillOpacity: .9,
  });
  m.bindPopup("<b>" + p.feeder + "</b><br>" + (p.kind === "pole" ? "Pole " : "Cabinet ") + p.where +
    "<br>" + p.phases + "-phase, permitted " + p.kw + " kW");
  m.addTo(groups[p.feeder]);
  bounds.push([p.lat, p.lon]);
});
bounds.push([sub.lat, sub.lon]);
map.fitBounds(bounds, { padding: [30, 30] });

const counts = {};
DATA.points.forEach(p => counts[p.feeder] = (counts[p.feeder] || 0) + 1);
const legend = document.getElementById("legend");
Object.keys(COLORS).forEach(f => {
  const label = document.createElement("label");
  label.innerHTML = '<input type="checkbox" checked> <span class="sw" style="background:' + COLORS[f] + '"></span> ' +
    f + ' <span class="muted">(' + counts[f] + ')</span>';
  label.querySelector("input").onchange = e => { e.target.checked ? groups[f].addTo(map) : map.removeLayer(groups[f]); };
  legend.appendChild(label);
});

function km(a, b) {
  const R = 6371, dLat = (b[0] - a[0]) * Math.PI / 180, dLon = (b[1] - a[1]) * Math.PI / 180;
  const s = Math.sin(dLat / 2) ** 2 + Math.cos(a[0] * Math.PI / 180) * Math.cos(b[0] * Math.PI / 180) * Math.sin(dLon / 2) ** 2;
  return 2 * R * Math.asin(Math.sqrt(s));
}
let pin = null;
map.on("click", e => {
  if (pin) map.removeLayer(pin);
  pin = L.marker(e.latlng, { icon: L.divIcon({ className: "", html: '<div style="width:18px;height:18px;background:#14213d;border:3px solid #ffd166;border-radius:50% 50% 50% 0;transform:rotate(-45deg) translate(2px,-6px)"></div>', iconSize: [18, 18], iconAnchor: [9, 16] }) }).addTo(map);
  const here = [e.latlng.lat, e.latlng.lng];
  const ranked = DATA.points.map(p => ({ p, d: km(here, [p.lat, p.lon]) })).sort((a, b) => a.d - b.d);
  const near = ranked[0];
  const same = ranked.filter(x => x.p.feeder === near.p.feeder).slice(0, 3);
  const toSub = km(here, [sub.lat, sub.lon]);
  document.getElementById("note").style.display = "none";
  const box = document.getElementById("result");
  box.style.display = "block";
  box.innerHTML =
    "<h2>New request dropped here</h2>" +
    "<p class='muted'>" + here[0].toFixed(5) + ", " + here[1].toFixed(5) + " &middot; " + (toSub * 1000).toFixed(0) + " m from the station</p>" +
    "<p>Nearest existing point is on <span class='pill' style='background:" + COLORS[near.p.feeder] + "'>" + near.p.feeder + "</span></p>" +
    "<p>" + (near.d * 1000).toFixed(0) + " m away, at " + (near.p.kind === "pole" ? "pole " : "cabinet ") + near.p.where +
    " (" + near.p.phases + "-phase, " + near.p.kw + " kW permitted).</p>" +
    "<p class='muted'>Closest points on that feeder: " + same.map(x => (x.d * 1000).toFixed(0) + " m").join(", ") + ".</p>" +
    "<p><b>This is all step 1 decides:</b> which feeder, and which pole or cabinet, the request belongs to. Conductor, length and the checks come after.</p>";
});
</script>
</body>
</html>
"""

OUT.parent.mkdir(exist_ok=True)
OUT.write_text(TEMPLATE.replace("__DATA__", json.dumps(data, ensure_ascii=False)), encoding="utf-8")
print(f"{len(points)} points -> {OUT}")

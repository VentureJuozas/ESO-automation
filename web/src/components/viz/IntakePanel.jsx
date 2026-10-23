import { useCallback, useEffect, useState } from "react";
import { getJSON } from "../../api.js";
import MapPanel from "../MapPanel.jsx";

export default function IntakePanel({ form, setForm, samples = [], onStart, running }) {
  const [tab, setTab] = useState("text");
  const [network, setNetwork] = useState(null);

  useEffect(() => {
    getJSON("/api/network").then(setNetwork).catch(() => {});
  }, []);

  const onPick = useCallback((pt) => {
    setForm((f) => ({ ...f, lat: pt.lat, lon: pt.lon }));
  }, [setForm]);

  const map = {
    request: { lat: Number(form.lat) || 54.55929, lon: Number(form.lon) || 25.27955 },
    selected: null,
    substation: network?.substation,
    elements: network?.elements || [],
    feeders: network?.feeders || [],
    line: { name: "L-200", path: [] },
  };

  return (
    <div className="intake">
      <header className="intake-head">
        <div>
          <div className="kicker">Nauja paraiška</div>
          <h2>Įklijuokite laišką arba užpildykite formą</h2>
        </div>
        <button className="exec" type="button" onClick={onStart} disabled={running}>Paleisti eigą</button>
      </header>
      <div className="sample-row">
        {(samples || []).map((s) => (
          <button
            key={s.id}
            type="button"
            className="go"
            onClick={() => { setForm((f) => ({ ...f, text: s.text })); setTab("text"); }}
          >
            {s.title}
          </button>
        ))}
      </div>
      <div className="tabs" role="tablist">
        <button type="button" className={tab === "text" ? "on" : ""} onClick={() => setTab("text")}>Laisvas tekstas</button>
        <button type="button" className={tab === "form" ? "on" : ""} onClick={() => setTab("form")}>Trumpa forma</button>
        <button type="button" className={tab === "map" ? "on" : ""} onClick={() => setTab("map")}>Taškas žemėlapyje</button>
      </div>
      {tab === "text" && (
        <textarea
          className="edit intake-text"
          value={form.text}
          onChange={(e) => setForm({ ...form, text: e.target.value })}
          placeholder="Sveiki, prašome prijungimo sąlygų…"
        />
      )}
      {tab === "form" && (
        <div className="form">
          <div><label>kW</label><input value={form.kw} onChange={(e) => setForm({ ...form, kw: Number(e.target.value) })} /></div>
          <div>
            <label>Fazės</label>
            <select value={form.phases} onChange={(e) => setForm({ ...form, phases: Number(e.target.value) })}>
              <option value={1}>1F</option>
              <option value={3}>3F</option>
            </select>
          </div>
          <div><label>Platuma</label><input value={form.lat} onChange={(e) => setForm({ ...form, lat: Number(e.target.value) })} /></div>
          <div><label>Ilguma</label><input value={form.lon} onChange={(e) => setForm({ ...form, lon: Number(e.target.value) })} /></div>
          <div className="full">
            <label>Objekto pavadinimas (be asmens duomenų)</label>
            <input value={form.object_name} onChange={(e) => setForm({ ...form, object_name: e.target.value })} />
          </div>
        </div>
      )}
      {tab === "map" && <MapPanel map={map} pickable onPick={onPick} />}
      <p className="map-note">Offline veikia deterministinis parseris. Asmens duomenys nerenkami — tik redaguoti laukai.</p>
    </div>
  );
}

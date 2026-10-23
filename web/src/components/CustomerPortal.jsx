import { useEffect, useState } from "react";
import { getJSON, postJSON } from "../api.js";
import MapPanel from "./MapPanel.jsx";

const STEPS = ["gauta", "tikrinama", "laukia inžinieriaus", "išduota"];

export default function CustomerPortal({ compact = false }) {
  const [net, setNet] = useState(null);
  const [form, setForm] = useState({ kw: 11, phases: 3, lat: 54.55929, lon: 25.27955, object_name: "Sodyba (redaguota)" });
  const [noCoord, setNoCoord] = useState(false);
  const [app, setApp] = useState(null);
  const [busy, setBusy] = useState(false);
  const [err, setErr] = useState("");

  useEffect(() => {
    getJSON("/api/network").then((n) => setNet({
      substation: n.substation,
      elements: n.elements,
      feeders: n.feeders,
      request: { lat: form.lat, lon: form.lon },
    })).catch(() => {});
  }, []);

  async function submit(e) {
    e?.preventDefault();
    setBusy(true);
    setErr("");
    try {
      const payload = noCoord ? { ...form, lat: null, lon: null } : form;
      const created = await postJSON("/api/portal/applications", payload);
      setApp(created);
    } catch (ex) {
      setErr(String(ex.message || ex));
    } finally {
      setBusy(false);
    }
  }

  useEffect(() => {
    if (!app?.id || app.status === "išduota") return undefined;
    const t = setInterval(() => {
      getJSON(`/api/portal/applications/${app.id}`).then(setApp).catch(() => {});
    }, 1200);
    return () => clearInterval(t);
  }, [app?.id, app?.status]);

  async function answer() {
    setBusy(true);
    try {
      const next = await postJSON(`/api/portal/applications/${app.id}/answer`, {
        lat: 54.55929,
        lon: 25.27955,
        kw: form.kw,
        phases: form.phases,
        text: "Koordinatės pateiktos per portalą.",
      });
      setApp(next);
    } finally {
      setBusy(false);
    }
  }

  const map = net ? { ...net, request: { lat: form.lat, lon: form.lon } } : null;
  const idx = STEPS.indexOf(app?.status === "laukia duomenų" || app?.status === "perduota inžinieriui" ? "tikrinama" : (app?.status || ""));

  return (
    <div className={`portal${compact ? " compact" : ""}`}>
      <div className="portal-banner">Demonstracinis maketas · neoficialus ESO portalas · be asmens duomenų</div>
      <header className="portal-head">
        <div>
          <div className="kicker">Buitinis prijungimas</div>
          <h2>Pateikti paraišką</h2>
        </div>
      </header>
      {!app && (
        <form className="portal-form" onSubmit={submit}>
          <label>Objektas
            <input value={form.object_name} onChange={(e) => setForm({ ...form, object_name: e.target.value })} />
          </label>
          <label>Adresas
            <input value="Adresas redaguotas · tik koordinatės" readOnly />
          </label>
          <div className="portal-row">
            <label>kW
              <input type="number" min="1" max="250" value={form.kw} onChange={(e) => setForm({ ...form, kw: Number(e.target.value) })} />
            </label>
            <label>Fazės
              <select value={form.phases} onChange={(e) => setForm({ ...form, phases: Number(e.target.value) })}>
                <option value={1}>1</option>
                <option value={3}>3</option>
              </select>
            </label>
          </div>
          <label className="portal-check">
            <input type="checkbox" checked={noCoord} onChange={(e) => setNoCoord(e.target.checked)} />
            Neturiu koordinačių — operatorius paprašys
          </label>
          {!noCoord && map && (
            <MapPanel map={map} pickable onPick={(p) => setForm((f) => ({ ...f, lat: p.lat, lon: p.lon }))} />
          )}
          <p className="hint">{noCoord ? "Pateikus, eiga sustos prie request_missing_data." : "Spustelėkite žemėlapį. Gatvės nerenkame."}</p>
          {err && <p className="hint">{err}</p>}
          <button className="exec" type="submit" disabled={busy}>Pateikti paraišką</button>
        </form>
      )}
      {app && (
        <div className="portal-track">
          <ol>
            {STEPS.map((s, i) => (
              <li key={s} className={i <= idx ? "on" : ""}>{s}</li>
            ))}
          </ol>
          <p className="hint">Būsena: <b>{app.status}</b>. {app.address}</p>
          {app.status === "laukia duomenų" && (
            <div className="missing-box">
              <p>Operatorius prašo koordinačių. Laiškas neišsiųstas — atsakykite čia.</p>
              <pre className="letter">{app.missing?.letter?.body}</pre>
              <button className="exec" type="button" disabled={busy} onClick={answer}>Pateikti koordinates ir tęsti</button>
            </div>
          )}
          {app.status === "išduota" && (
            <div className="inbox-actions">
              <a className="exec" href={app.ts_url} target="_blank" rel="noreferrer">Atidaryti TS</a>
              <a className="go" href={app.pdf_url}>Atsisiųsti PDF</a>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

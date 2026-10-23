import { useEffect, useState } from "react";
import { getJSON, postJSON } from "../api.js";
import MapPanel from "./MapPanel.jsx";

const STEPS = ["gauta", "tikrinama", "laukia duomenų", "laukia inžinieriaus", "išduota"];

function when(ts) {
  if (!ts) return "—";
  return new Date(ts * 1000).toLocaleString("lt-LT", {
    day: "2-digit",
    month: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
  });
}

function stepClass(step, app) {
  const tl = (app.timeline || []).map((x) => x.status);
  if (app.status === step) return "on current";
  if (tl.includes(step)) return "on";
  const order = STEPS.indexOf(step);
  const cur = STEPS.indexOf(app.status);
  if (step === "laukia duomenų" && cur > order && !tl.includes(step)) return "skip";
  if (cur > order) return "on";
  return "";
}

export default function CustomerPortal({ compact = false, onSubmitted }) {
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
      onSubmitted?.(created);
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
      onSubmitted?.(next);
    } finally {
      setBusy(false);
    }
  }

  const map = net ? { ...net, request: { lat: form.lat, lon: form.lon } } : null;

  return (
    <div className={`portal${compact ? " compact" : ""}`} data-testid="customer-portal">
      <div className="portal-banner">Demonstracinis maketas, neoficialus ESO portalas, be asmens duomenų</div>
      <header className="portal-head">
        <div>
          <div className="kicker">Buitinis prijungimas</div>
          <h2>{app ? "Paraiškos būsena" : "Pateikti paraišką"}</h2>
        </div>
      </header>
      {!app && (
        <form className="portal-form" onSubmit={submit} data-testid="customer-form">
          <label>Objektas
            <input data-testid="portal-object" value={form.object_name} onChange={(e) => setForm({ ...form, object_name: e.target.value })} />
          </label>
          <label>Adresas
            <input value="Adresas redaguotas, tik koordinatės" readOnly />
          </label>
          <div className="portal-row">
            <label>kW
              <input data-testid="portal-kw" type="number" min="1" max="250" value={form.kw} onChange={(e) => setForm({ ...form, kw: Number(e.target.value) })} />
            </label>
            <label>Fazės
              <select data-testid="portal-phases" value={form.phases} onChange={(e) => setForm({ ...form, phases: Number(e.target.value) })}>
                <option value={1}>1</option>
                <option value={3}>3</option>
              </select>
            </label>
          </div>
          <label className="portal-check">
            <input type="checkbox" data-testid="portal-nocoord" checked={noCoord} onChange={(e) => setNoCoord(e.target.checked)} />
            Neturiu koordinačių — operatorius paprašys
          </label>
          {!noCoord && map && (
            <MapPanel map={map} pickable onPick={(p) => setForm((f) => ({ ...f, lat: p.lat, lon: p.lon }))} />
          )}
          <p className="hint">{noCoord ? "Pateikus, eiga sustos prie request_missing_data." : "Spustelėkite žemėlapį. Gatvės nerenkame."}</p>
          {err && <p className="hint">{err}</p>}
          <button className="exec" type="submit" disabled={busy} data-testid="portal-submit">Pateikti paraišką</button>
        </form>
      )}
      {app && (
        <div className="portal-status" data-testid="customer-tracker">
          <div className="portal-card">
            <div className="kicker">Santrauka</div>
            <b data-testid="portal-object-name">{app.object_name}</b>
            <p>{app.kw} kW, {app.phases}F, {app.address}</p>
            <p className="hint">Nr. {app.id}, {app.customer}</p>
            <p data-testid="portal-status">Būsena: <b>{app.status}</b></p>
            {app.decision_by && (
              <p data-testid="portal-sla">Sprendimo data (SLA): <b>{when(app.decision_by)}</b>, {app.sla?.days} d. d.</p>
            )}
          </div>
          <ol className="portal-timeline" data-testid="portal-timeline">
            {STEPS.map((s) => {
              const hit = (app.timeline || []).find((x) => x.status === s);
              return (
                <li key={s} className={stepClass(s, app)} data-step={s}>
                  <b>{s}</b>
                  <small>{hit ? when(hit.at) : stepClass(s, app) === "skip" ? "praleista" : "—"}</small>
                </li>
              );
            })}
          </ol>
          {app.status === "laukia duomenų" && (
            <div className="missing-box" data-testid="portal-missing">
              <p>Operatorius prašo koordinačių. Laiškas neišsiųstas — atsakykite čia.</p>
              <pre className="letter">{app.missing?.letter?.body}</pre>
              <button className="exec" type="button" disabled={busy} data-testid="portal-answer" onClick={answer}>Pateikti koordinates ir tęsti</button>
            </div>
          )}
          {app.status === "išduota" && (
            <div className="portal-card download" data-testid="portal-download">
              <div className="kicker">Techninės sąlygos</div>
              <b>Išduota — galite atsisiųsti</b>
              <div className="inbox-actions">
                <a className="exec" href={app.ts_url} target="_blank" rel="noreferrer">Atidaryti TS</a>
                <a className="go" data-testid="portal-pdf" href={app.pdf_url}>Atsisiųsti PDF</a>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

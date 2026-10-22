import { useEffect, useState } from "react";
import SourceTags from "./SourceTags.jsx";
import TransformerBar from "./viz/TransformerBar.jsx";
import VoltageProfile from "./viz/VoltageProfile.jsx";
import AffectedList from "./viz/AffectedList.jsx";
import HeadroomGauge from "./viz/HeadroomGauge.jsx";
import SolutionCards from "./viz/SolutionCards.jsx";
import TsDocument from "./viz/TsDocument.jsx";
import CostTable from "./viz/CostTable.jsx";
import MapPanel from "./MapPanel.jsx";

function statusBadge(ev, running) {
  if (running) return <span className="badge">Vykdoma</span>;
  if (!ev) return <span className="badge">Laukia</span>;
  if (ev.type === "interrupt") return <span className="badge human">Laukia inžinieriaus</span>;
  if (ev.outputs?.escalate) return <span className="badge bad">Nepraeina</span>;
  if (ev.outputs?.pass === false) return <span className="badge bad">Nepraeina</span>;
  if (ev.ok === false) return <span className="badge bad">Klaida</span>;
  return <span className="badge ok">Atlikta</span>;
}

function Viz({ ev, section3, setSection3, canEdit }) {
  const o = ev?.outputs || {};
  switch (ev?.tool) {
    case "check_capacity":
      return <TransformerBar bar={o.transformer_bar} pass={o.pass} />;
    case "check_voltage_drop":
      return <VoltageProfile profile={o.profile} limit={o.limit_v} />;
    case "check_reliability":
      return <AffectedList cutIn={o.cut_in} n1={o.n1} backup={o.backup} />;
    case "check_future":
      return <HeadroomGauge gauge={o.gauge} />;
    case "select_solution":
      return <SolutionCards comparison={o.comparison} chosen={o} />;
    case "draft_ts_section3":
    case "engineer_approval":
    case "issue_ts":
      return <TsDocument document={o.document || o.application && { ...o, section3: o.section3 }} section3={section3} onChange={setSection3} editable={canEdit} />;
    case "estimate_cost":
      return <CostTable cost={o} />;
    case "render_map":
      return <MapPanel map={o} />;
    default:
      return null;
  }
}

function RequestParams({ form, setForm }) {
  if (!form || !setForm) return null;
  return (
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
        <label>Laisvas tekstas (LLM / replay skaitymui)</label>
        <input value={form.text} onChange={(e) => setForm({ ...form, text: e.target.value })} />
      </div>
    </div>
  );
}

export default function StepSheet({
  toolId, event, running, error, catalog, onRerun, section3, setSection3, canEdit, emptyHint,
  form, setForm, onClose,
}) {
  const [tab, setTab] = useState("output");
  const meta = (catalog?.tools || []).find((t) => t.id === toolId) || {};
  const showForm = toolId === "parse_request" && form && setForm;

  useEffect(() => {
    setTab(showForm && !event ? "params" : "output");
  }, [toolId, event, showForm]);

  if (error) {
    return (
      <section className="sheet" role="region" aria-label="Žingsnio lapas">
        <div className="sheet-body"><div className="error">{error}</div></div>
      </section>
    );
  }
  if (running && !event) {
    return (
      <section className="sheet" role="region" aria-busy="true">
        <header className="sheet-head">
          <div>
            <div className="sheet-kicker">{toolId}</div>
            <h2>{meta.title_lt || toolId}</h2>
          </div>
          {onClose && <button type="button" className="insp-x" onClick={onClose} aria-label="Uždaryti">×</button>}
        </header>
        <div className="sheet-body">
          <div className="skel"><div className="skel-bar" /><div className="skel-bar" /><div className="skel-bar" /></div>
        </div>
      </section>
    );
  }
  if (!event && !toolId) {
    return (
      <section className="sheet" role="region">
        <div className="empty">{emptyHint || "Paleiskite eigą arba pasirinkite žingsnį."}</div>
      </section>
    );
  }
  const title = event?.title_lt || event?.title || meta.title_lt || toolId;
  const inputs = event?.inputs || {};
  const callName = event?.tool || toolId;
  return (
    <section className="sheet" role="region" aria-label={title}>
      <header className="sheet-head">
        <div>
          <div className="sheet-kicker">{callName}</div>
          <h2>{title}</h2>
        </div>
        <div className="badges">
          {statusBadge(event, running)}
          {event?.llm && <span className="badge llm">LLM</span>}
          {(event?.kind === "human" || meta.kind === "human") && <span className="badge human">Žmogus</span>}
          {(event?.kind === "tool" || meta.kind === "tool") && <span className="badge">Python</span>}
          {event?.elapsed_ms != null && <span className="badge">{event.elapsed_ms} ms</span>}
          {onClose && <button type="button" className="insp-x" onClick={onClose} aria-label="Uždaryti">×</button>}
        </div>
      </header>
      <div className="tabs" role="tablist">
        <button type="button" className={tab === "output" ? "on" : ""} onClick={() => setTab("output")}>Išvestis</button>
        <button type="button" className={tab === "params" ? "on" : ""} onClick={() => setTab("params")}>Parametrai</button>
        <button type="button" className={tab === "json" ? "on" : ""} onClick={() => setTab("json")}>JSON</button>
      </div>
      <div className="sheet-body">
        {(event?.engineer || meta.engineer) && <p className="hint">{event?.engineer || meta.engineer}</p>}
        {tab === "output" && (
          <>
            <Viz ev={event} section3={section3} setSection3={setSection3} canEdit={canEdit} />
            {event?.outputs?.reason && event.outputs.escalate && (
              <p className="hint" style={{ borderColor: "var(--bad)" }}>{event.outputs.reason}</p>
            )}
            {!event && showForm && <p className="empty" style={{ padding: 12 }}>Paleiskite eigą — šio mazgo išvestis atsiras čia.</p>}
          </>
        )}
        {tab === "params" && (
          <div className="section">
            <h3>Įvestis ir kvietimas</h3>
            {showForm && <RequestParams form={form} setForm={setForm} />}
            {Object.keys(inputs).length > 0 && (
              <div className="kv" style={{ marginTop: showForm ? 12 : 0 }}>
                {Object.entries(inputs).slice(0, 10).map(([k, v]) => (
                  <div key={k}><b>{k}</b><span>{typeof v === "object" ? JSON.stringify(v) : String(v)}</span></div>
                ))}
              </div>
            )}
            {event && (
              <div className="toolcall" style={{ marginTop: 10 }}>
                <span className="fn">{callName}</span>
                ({JSON.stringify(inputs)})
              </div>
            )}
          </div>
        )}
        {tab === "json" && <pre className="json">{JSON.stringify(event?.outputs ?? meta, null, 2)}</pre>}
        <div className="section">
          <h3>Šaltiniai ir taisyklė</h3>
          <SourceTags tags={event?.source_tags} />
          {(event?.rule_ref || meta.rule_ref) && (
            <p className="rule" style={{ marginTop: 8 }}>
              <a href={(event?.rule_ref || meta.rule_ref).url} target="_blank" rel="noreferrer">{(event?.rule_ref || meta.rule_ref).label} ↗</a>
              {(event?.rule_ref || meta.rule_ref).local && <span style={{ color: "var(--muted)" }}> · {(event?.rule_ref || meta.rule_ref).local}</span>}
            </p>
          )}
          {(event?.notes || []).filter(Boolean).map((n) => <p key={n} style={{ color: "var(--muted)", fontSize: 12 }}>{n}</p>)}
        </div>
        {onRerun && event?.tool && event.tool !== "engineer_approval" && (
          <button className="go" type="button" onClick={() => onRerun(event.tool)}>Perskaičiuoti nuo čia</button>
        )}
      </div>
    </section>
  );
}

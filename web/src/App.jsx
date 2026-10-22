import { useEffect, useMemo, useRef, useState } from "react";
import { connectEvents, getJSON, postJSON } from "./api.js";
import { Icon } from "./icons.jsx";
import WorkflowCanvas from "./components/WorkflowCanvas.jsx";
import StepSheet from "./components/StepSheet.jsx";
import HowItWorks from "./components/HowItWorks.jsx";
import RuleSheet from "./components/RuleSheet.jsx";
import SourceTags from "./components/SourceTags.jsx";
import { scenarioStickies } from "./workflow.js";

const EMPTY_FORM = { kw: 11, phases: 3, lat: 54.55929, lon: 25.27955, text: "", pending_kw: 0, object_name: "Naujas buitinis objektas" };

export default function App() {
  const [view, setView] = useState("case");
  const [scenarios, setScenarios] = useState([]);
  const [history, setHistory] = useState([]);
  const [architecture, setArchitecture] = useState(null);
  const [scenarioId, setScenarioId] = useState("hero");
  const [form, setForm] = useState(EMPTY_FORM);
  const [run, setRun] = useState(null);
  const [events, setEvents] = useState([]);
  const [runningTool, setRunningTool] = useState(null);
  const [selected, setSelected] = useState("parse_request");
  const [section3, setSection3] = useState("");
  const [error, setError] = useState("");
  const [open, setOpen] = useState({ paraiskos: true, istorija: true, kita: true });
  const [inspectorOpen, setInspectorOpen] = useState(true);
  const stopRef = useRef(() => {});

  useEffect(() => {
    getJSON("/api/scenarios").then(setScenarios).catch((e) => setError(String(e)));
    getJSON("/api/architecture").then(setArchitecture).catch(() => {});
    getJSON("/api/runs").then(setHistory).catch(() => {});
  }, []);

  const current = scenarios.find((s) => s.id === scenarioId);
  const snap = run;
  const failed = Boolean(snap?.failed);
  const status = snap?.status || "idle";
  const value = snap?.value;
  const selectedEvent = useMemo(
    () => [...events].reverse().find((e) => e.tool === selected && e.type !== "start") || null,
    [events, selected]
  );

  useEffect(() => {
    const s3 = snap?.draft?.section3 || snap?.issued?.section3;
    if (s3 && !section3) setSection3(s3);
  }, [snap?.draft, snap?.issued]);

  function pickNode(id) {
    setSelected(id);
    setInspectorOpen(true);
  }

  function pickScenario(s) {
    setScenarioId(s.id);
    setView("case");
    setForm({ ...EMPTY_FORM, ...s.form });
    setRun(null);
    setEvents([]);
    setSection3("");
    setSelected("parse_request");
    setInspectorOpen(true);
    setError("");
  }

  async function start() {
    setError("");
    setEvents([]);
    setSection3("");
    setRunningTool("parse_request");
    setSelected("parse_request");
    setInspectorOpen(true);
    stopRef.current();
    try {
      const created = await postJSON("/api/runs", { scenario_id: scenarioId, text: form.text, form });
      setRun(created);
      const close = connectEvents(
        created.id,
        (ev) => {
          if (ev.type === "start") {
            setRunningTool(ev.tool);
            setSelected(ev.tool);
            setInspectorOpen(true);
          } else if (ev.type === "tool") {
            setEvents((xs) => [...xs, ev]);
            setRunningTool(null);
            setSelected(ev.tool);
          } else if (ev.type === "interrupt") {
            setEvents((xs) => [...xs, ev]);
            setRunningTool(null);
            setSelected("engineer_approval");
            setInspectorOpen(true);
          } else if (ev.type === "status" || ev.type === "done") {
            if (ev.snapshot) {
              setRun(ev.snapshot);
              if (ev.snapshot.draft?.section3) setSection3(ev.snapshot.draft.section3);
            } else {
              getJSON(`/api/runs/${created.id}`).then(setRun);
            }
            if (ev.type === "done") setRunningTool(null);
            getJSON("/api/runs").then(setHistory).catch(() => {});
          } else if (ev.type === "error") {
            setError(ev.message || "Klaida");
            setRunningTool(null);
          }
        },
        () => {}
      );
      stopRef.current = close;
    } catch (e) {
      setError(String(e));
      setRunningTool(null);
    }
  }

  async function approve(force = false) {
    if (!run?.id) return;
    setRunningTool("issue_ts");
    setSelected("issue_ts");
    const snap2 = await postJSON(`/api/runs/${run.id}/resume`, {
      decision: "approve",
      section3,
      force,
    });
    setRun(snap2);
    setEvents(snap2.events || events);
    setRunningTool(null);
    setSelected("issue_ts");
    getJSON("/api/runs").then(setHistory).catch(() => {});
  }

  async function saveEdit() {
    if (!run?.id) return;
    const snap2 = await postJSON(`/api/runs/${run.id}/resume`, { decision: "edit", section3 });
    setRun(snap2);
    setEvents(snap2.events || events);
  }

  async function rerun(fromTool) {
    if (!run?.id) return;
    setRunningTool(fromTool);
    const snap2 = await postJSON(`/api/runs/${run.id}/rerun`, {
      from_tool: fromTool,
      overrides: { pending_kw: form.pending_kw, kw: form.kw, phases: form.phases, lat: form.lat, lon: form.lon },
    });
    setRun(snap2);
    setEvents(snap2.events || []);
    setRunningTool(null);
  }

  const waiting = status === "awaiting_approval" || status === "escalated";
  const llmMode = architecture?.llm_mode || snap?.llm_mode || "offline";
  const hud = runningTool
    ? { cls: "run", text: `Vykdoma · ${runningTool}` }
    : waiting
      ? { cls: failed ? "bad" : "wait", text: failed ? "Sustabdyta · eskalacija" : "Sustabdyta · inžinieriaus vartai" }
      : status === "issued"
        ? { cls: "ok", text: "Išduota · TS paruošta spausdinti" }
        : { cls: "", text: "Drobė · spustelėkite mazgą" };

  return (
    <div className="app">
      <aside className="side">
        <div className="brand">
          <span className="mark"><Icon name="branch" size={16} /></span>
          <div><b>Sąlygos</b><small>Prijungimo eiga</small></div>
        </div>
        <nav className="nav">
          <div className={`sec${open.paraiskos ? " open" : ""}`}>
            <button className={`sec-btn${open.paraiskos ? " open" : ""}`} type="button" onClick={() => setOpen((o) => ({ ...o, paraiskos: !o.paraiskos }))}>
              Scenarijai <span className="count">{scenarios.length}</span>
            </button>
            {open.paraiskos && scenarios.map((s) => (
              <button key={s.id} className={`item${view === "case" && scenarioId === s.id ? " on" : ""}`} type="button" onClick={() => pickScenario(s)}>
                <b>{s.title}</b>
                <small>{s.subtitle}</small>
              </button>
            ))}
          </div>
          <div className={`sec${open.istorija ? " open" : ""}`}>
            <button className={`sec-btn${open.istorija ? " open" : ""}`} type="button" onClick={() => setOpen((o) => ({ ...o, istorija: !o.istorija }))}>
              Istorija <span className="count">{history.length}</span>
            </button>
            {open.istorija && history.map((h) => (
              <button key={h.id} className="item" type="button" onClick={() => getJSON(`/api/runs/${h.id}`).then((r) => { setRun(r); setEvents(r.events || []); setView("case"); setSelected("parse_request"); setInspectorOpen(true); })}>
                <b>{h.id.slice(0, 6)} · {h.solution || "—"} {h.kw} kW</b>
                <small>{h.status}</small>
              </button>
            ))}
          </div>
          <div className={`sec${open.kita ? " open" : ""}`}>
            <button className={`sec-btn${open.kita ? " open" : ""}`} type="button" onClick={() => setOpen((o) => ({ ...o, kita: !o.kita }))}>
              Kita
            </button>
            {open.kita && (
              <>
                <button className={`item${view === "how" ? " on" : ""}`} type="button" onClick={() => { setView("how"); setSelected("ui"); setInspectorOpen(true); }}>
                  <b>Kaip tai veikia</b><small>Architektūros drobė</small>
                </button>
                <button className={`item${view === "rules" ? " on" : ""}`} type="button" onClick={() => { setView("rules"); setSelected("parse_request"); setInspectorOpen(true); }}>
                  <b>Taisyklės</b><small>Mazgai ir ESO šaltiniai</small>
                </button>
              </>
            )}
          </div>
        </nav>
        <p className="side-note">Skaičiai iš TP 12-608. Kainos — orientyras iš 26-E-37934. LLM: {llmMode}. Be asmens duomenų.</p>
      </aside>

      <section className="main">
        <header className="top">
          <div className="crumb">
            {view === "how" ? "Kaip tai veikia" : view === "rules" ? "Taisyklės" : <>Paraiškos <span>/</span> {current?.title || "Naujas vartotojas, TP 12-608"}</>}
          </div>
          <div className="top-actions">
            <span className="badge">{llmMode === "offline" ? "Replay / be rakto" : `LLM ${llmMode}`}</span>
            {view === "case" && (
              <>
                {status === "issued" && run?.id && (
                  <a className="go" href={`/api/runs/${run.id}/ts.html`} target="_blank" rel="noreferrer">Atidaryti TS</a>
                )}
                <button className="exec" type="button" onClick={start} disabled={status === "running" || Boolean(runningTool)}>Paleisti eigą</button>
              </>
            )}
          </div>
        </header>

        {view === "case" && (
          <div className="value">
            <div className="v"><b>{value ? `${(value.elapsed_ms / 1000).toFixed(1)} s` : "—"}</b><span>agento eiga</span></div>
            <div className="v"><b>2–4 val.</b><span>rankinis (prielaida)</span></div>
            <div className="v"><b>{value?.tools_run ?? 0}</b><span>įrankių / taisyklių</span></div>
            <div className="v"><SourceTags tags={Object.keys(value?.source_counts || {})} /></div>
            <p className="assume">{architecture?.manual_time_note}</p>
          </div>
        )}

        <div className="canvas" style={{ flex: 1, minHeight: 0, display: "flex", flexDirection: "column" }}>
          {view === "case" && <div className={`exec-hud ${hud.cls}`}>{hud.text}</div>}
          <div className="workspace">
            <div className="wf-wrap">
              {view === "case" && (
                <WorkflowCanvas
                  events={events}
                  runningTool={runningTool}
                  failed={failed}
                  selectedId={selected}
                  onSelect={pickNode}
                  stickies={scenarioStickies(current)}
                  inspectorOpen={inspectorOpen}
                  followId={runningTool}
                />
              )}
              {view === "how" && (
                <WorkflowCanvas
                  mode="arch"
                  selectedId={selected}
                  onSelect={pickNode}
                  architecture={architecture}
                  inspectorOpen={inspectorOpen}
                />
              )}
              {view === "rules" && (
                <WorkflowCanvas
                  events={[]}
                  selectedId={selected}
                  onSelect={pickNode}
                  inspectorOpen={inspectorOpen}
                  stickies={[{ id: "rules-note", x: 36, y: 516, title: "Taisyklės prie mazgų", body: "Spustelėkite mazgą — dešinėje n8n skydelyje ESO šaltinis, įvestis ir ką tikrinti inžinieriui." }]}
                />
              )}
            </div>
            {inspectorOpen ? (
              <div className="inspector">
                {view === "case" && (
                  <StepSheet
                    toolId={selected}
                    event={selectedEvent}
                    running={runningTool === selected}
                    error={error}
                    catalog={architecture}
                    onRerun={run?.id ? rerun : null}
                    section3={section3}
                    setSection3={setSection3}
                    canEdit={waiting}
                    form={form}
                    setForm={setForm}
                    onClose={() => setInspectorOpen(false)}
                    emptyHint="Paleiskite eigą. Mazgai ant drobės užsidegs paeiliui kaip n8n."
                  />
                )}
                {view === "how" && (
                  <section className="sheet">
                    <header className="sheet-head">
                      <div>
                        <div className="sheet-kicker">{selected}</div>
                        <h2>{(architecture?.layers || []).find((l) => l.id === selected)?.title || "Kaip tai veikia"}</h2>
                      </div>
                      <button type="button" className="insp-x" onClick={() => setInspectorOpen(false)} aria-label="Uždaryti">×</button>
                    </header>
                    <div className="sheet-body">
                      <HowItWorks architecture={architecture} layerId={selected} />
                    </div>
                  </section>
                )}
                {view === "rules" && (
                  <section className="sheet">
                    <header className="sheet-head">
                      <div>
                        <div className="sheet-kicker">{selected}</div>
                        <h2>{(architecture?.tools || []).find((t) => t.id === selected)?.title_lt || selected}</h2>
                      </div>
                      <button type="button" className="insp-x" onClick={() => setInspectorOpen(false)} aria-label="Uždaryti">×</button>
                    </header>
                    <div className="sheet-body">
                      <RuleSheet toolId={selected} catalog={architecture} />
                    </div>
                  </section>
                )}
              </div>
            ) : (
              <button type="button" className="insp-reopen" onClick={() => setInspectorOpen(true)}>Mazgas</button>
            )}
          </div>
          {view === "case" && waiting && (
            <div className={`dock${failed ? " bad" : ""}`}>
              <div>
                <b>{failed ? "Patikra nepraėjo — inžinieriui" : "Laukia inžinieriaus patvirtinimo"}</b>
                <div style={{ color: "var(--muted)", fontSize: 12 }}>
                  {failed ? snap?.escalate?.reasons?.join(" ") : "Peržiūrėkite §3 dešiniame skydelyje, tada išduokite."}
                </div>
              </div>
              <div style={{ display: "flex", gap: 8 }}>
                <button className="go" type="button" onClick={saveEdit}>Įrašyti §3 pataisą</button>
                {failed ? (
                  <button className="ink" type="button" onClick={() => approve(true)}>Išduoti vis tiek</button>
                ) : (
                  <button className="exec" type="button" onClick={() => approve(false)}>Patvirtinti ir išduoti</button>
                )}
              </div>
            </div>
          )}
        </div>
      </section>
    </div>
  );
}

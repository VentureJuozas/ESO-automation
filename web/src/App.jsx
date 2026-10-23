import { useEffect, useMemo, useRef, useState } from "react";
import { connectEvents, getJSON, postJSON } from "./api.js";
import WorkflowCanvas from "./components/WorkflowCanvas.jsx";
import StepSheet from "./components/StepSheet.jsx";
import Sidebar from "./components/Sidebar.jsx";
import TracePanel from "./components/TracePanel.jsx";
import { buildTrace } from "./trace.js";
import { GROUPS } from "./steps.js";

const HERO = {
  kw: 11,
  phases: 3,
  lat: 54.55929,
  lon: 25.27955,
  object_name: "Household connection",
  text: "New household customer, 11 kW, three phases, coordinates 54.55929, 25.27955, TP 12-608.",
};

export default function App() {
  const [architecture, setArchitecture] = useState(null);
  const [run, setRun] = useState(null);
  const [events, setEvents] = useState([]);
  const [runningTool, setRunningTool] = useState(null);
  const [selected, setSelected] = useState("parse_request");
  const [section3, setSection3] = useState("");
  const [error, setError] = useState("");
  const [inspectorOpen, setInspectorOpen] = useState(true);
  const [kindOverlay, setKindOverlay] = useState(false);
  const [groupsOpen, setGroupsOpen] = useState({
    application: true,
    connection: true,
    checks: true,
    solution: true,
    issue: true,
  });
  const stopRef = useRef(() => {});

  useEffect(() => {
    getJSON("/api/architecture").then(setArchitecture).catch((e) => setError(String(e)));
  }, []);

  const snap = run;
  const failed = Boolean(snap?.failed) && !snap?.overridden;
  const skipped = snap?.skipped || [];
  const status = snap?.status || "idle";
  const selectedEvent = useMemo(
    () => [...events].reverse().find((e) => e.tool === selected && e.type !== "start") || null,
    [events, selected]
  );
  const loadLoss = useMemo(() => {
    const cap = [...events].reverse().find((e) => e.tool === "check_capacity" && e.outputs?.load_loss);
    const volt = [...events].reverse().find((e) => e.tool === "check_voltage_drop" && e.outputs?.load_loss);
    return cap?.outputs?.load_loss || volt?.outputs?.load_loss || null;
  }, [events]);

  useEffect(() => {
    const s3 = snap?.draft?.section3 || snap?.issued?.section3;
    if (s3 && !section3) setSection3(s3);
  }, [snap?.draft, snap?.issued]);

  function pickNode(id) {
    setSelected(id);
    setInspectorOpen(true);
    const group = GROUPS.find((g) => g.tools.includes(id));
    if (group) setGroupsOpen((o) => ({ ...o, [group.id]: true }));
  }

  function listen(created) {
    stopRef.current();
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
          setSelected(ev.tool || "engineer_approval");
          setInspectorOpen(true);
          getJSON(`/api/runs/${created.id}`).then((r) => {
            setRun(r);
            if (r.events) setEvents(r.events);
          }).catch(() => {});
        } else if (ev.type === "status" || ev.type === "done") {
          if (ev.snapshot) {
            setRun(ev.snapshot);
            if (ev.snapshot.draft?.section3) setSection3(ev.snapshot.draft.section3);
            if (ev.snapshot.events) setEvents(ev.snapshot.events);
          } else {
            getJSON(`/api/runs/${created.id}`).then((r) => {
              setRun(r);
              if (r.events) setEvents(r.events);
            });
          }
          if (ev.type === "done") setRunningTool(null);
        } else if (ev.type === "error") {
          setError(ev.message || "Error");
          setRunningTool(null);
        }
      },
      () => {}
    );
    stopRef.current = close;
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
      const created = await postJSON("/api/runs", { scenario_id: "hero", text: HERO.text, form: HERO });
      setRun(created);
      listen(created);
      getJSON(`/api/runs/${created.id}`).then((r) => {
        if (r.status && r.status !== "queued" && r.status !== "running") {
          setRun(r);
          if (r.events) setEvents(r.events);
        }
      }).catch(() => {});
    } catch (e) {
      setError(String(e));
      setRunningTool(null);
    }
  }

  async function approve() {
    if (!run?.id) return;
    setRunningTool("issue_ts");
    setSelected("issue_ts");
    const snap2 = await postJSON(`/api/runs/${run.id}/resume`, { decision: "approve", section3 });
    setRun(snap2);
    setEvents(snap2.events || events);
    setRunningTool(null);
    setSelected("issue_ts");
  }

  async function saveEdit() {
    if (!run?.id) return;
    const snap2 = await postJSON(`/api/runs/${run.id}/resume`, { decision: "edit", section3 });
    setRun(snap2);
    setEvents(snap2.events || events);
  }

  const issuedDoc = snap?.issued?.document || snap?.draft?.document;
  const waiting = status === "awaiting_approval";
  const hud = status === "running" || runningTool
    ? { cls: "run", text: `Running · ${runningTool || "…"}` }
    : status === "awaiting_approval"
      ? { cls: "wait", text: "Awaiting engineer" }
      : status === "issued"
        ? { cls: "ok", text: snap?.issued?.ts_number || "Issued" }
        : { cls: "", text: "11 kW · 3F · L-200 · pole 200/3" };

  return (
    <div className="app">
      <Sidebar
        events={events}
        runningTool={runningTool}
        selected={selected}
        onSelect={pickNode}
        open={groupsOpen}
        onToggle={(id) => setGroupsOpen((o) => ({ ...o, [id]: !o[id] }))}
        status={status}
      />
      <section className="main">
        <header className="top">
          <div className="crumb" data-testid="app-title">ESO helper</div>
          <div className="top-actions">
            {status === "issued" && run?.id && (
              <a className="go" data-testid="open-ts" href={`/api/runs/${run.id}/ts.html`} target="_blank" rel="noreferrer">
                Prijungimo sąlygų dokumentas
              </a>
            )}
            {run?.id && (
              <a className="go" href={`/api/runs/${run.id}/audit.html`} target="_blank" rel="noreferrer">Audit</a>
            )}
            <button
              className={`go${kindOverlay ? " on" : ""}`}
              type="button"
              data-testid="nav-trace"
              onClick={() => { setKindOverlay((v) => !v); setInspectorOpen(true); }}
            >
              Trace
            </button>
            <button
              className="exec"
              type="button"
              data-testid="run-flow"
              onClick={start}
              disabled={status === "running" || Boolean(runningTool)}
            >
              Run
            </button>
          </div>
        </header>

        <div className="request-bar" data-testid="request-bar">
          <div><b>Request</b><span>11 kW · 3-phase</span></div>
          <div><b>Point</b><span>54.55929, 25.27955</span></div>
          <div><b>Network</b><span>TP 12-608 · L-200 · 200/3</span></div>
          <div><b>Solution</b><span>B · C 20 A</span></div>
        </div>

        <div className="canvas" style={{ flex: 1, minHeight: 0, display: "flex", flexDirection: "column" }}>
          <div className={`exec-hud ${hud.cls}`}>{hud.text}</div>
          <div className="workspace">
            <div className="wf-wrap">
              <WorkflowCanvas
                events={events}
                runningTool={runningTool}
                failed={failed}
                skipped={skipped}
                selectedId={selected}
                onSelect={pickNode}
                architecture={architecture}
                inspectorOpen={inspectorOpen}
                followId={runningTool}
                kindOverlay={kindOverlay}
                onToggleOverlay={(on) => { setKindOverlay(on); if (on) setInspectorOpen(true); }}
              />
            </div>
            {inspectorOpen ? (
              <div className="inspector">
                {kindOverlay ? (
                  <TracePanel
                    trace={buildTrace(events, architecture?.tools || [])}
                    selectedId={selected}
                    onSelect={pickNode}
                  />
                ) : (
                  <StepSheet
                    toolId={selected}
                    event={selectedEvent}
                    running={runningTool === selected}
                    error={error}
                    section3={section3}
                    setSection3={setSection3}
                    canEdit={waiting && !failed}
                    onClose={() => setInspectorOpen(false)}
                    runId={run?.id}
                    document={issuedDoc}
                    status={status}
                    loadLoss={loadLoss}
                  />
                )}
              </div>
            ) : (
              <button type="button" className="insp-reopen" onClick={() => setInspectorOpen(true)}>Panel</button>
            )}
          </div>
          {waiting && (
            <div className="dock" data-testid="approval-dock">
              <div>
                <b>Engineer approval</b>
                <div style={{ color: "var(--muted)", fontSize: 12 }}>§3 · audit · issue</div>
              </div>
              <div style={{ display: "flex", gap: 8 }}>
                {run?.id && <a className="go" href={`/api/runs/${run.id}/audit.html`} target="_blank" rel="noreferrer">Audit</a>}
                <button className="go" type="button" onClick={saveEdit}>Save §3</button>
                <button className="exec" type="button" data-testid="approve" onClick={approve}>Approve and issue</button>
              </div>
            </div>
          )}
        </div>
      </section>
    </div>
  );
}

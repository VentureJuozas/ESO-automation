import { useEffect, useMemo, useRef, useState } from "react";
import { connectEvents, getJSON, postJSON } from "./api.js";
import WorkflowCanvas from "./components/WorkflowCanvas.jsx";
import StepSheet from "./components/StepSheet.jsx";
import Sidebar from "./components/Sidebar.jsx";
import ChangeRequest from "./components/ChangeRequest.jsx";
import TestEnvironment from "./components/TestEnvironment.jsx";
import PowerRequest from "./components/PowerRequest.jsx";
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

const HERO_SUMMARY = {
  power: "11 kW, 3-phase",
  coords: "54.55929, 25.27955",
  network: "TP 12-608, feeder L-200, pole 200/3",
  solution: "New pole-mounted cabinet, 16 mm² service, 20 A breaker",
};

function eventOutput(events, tool) {
  const hit = [...events].reverse().find((event) => event.tool === tool && event.outputs);
  return hit?.outputs || null;
}

function coordText(value) {
  const number = Number(value);
  if (!Number.isFinite(number)) return "";
  return String(Math.round(number * 1e5) / 1e5);
}

function requestSummary(power, events) {
  if (!power) return HERO_SUMMARY;
  const location = eventOutput(events, "locate_connection_point");
  const solution = eventOutput(events, "select_solution");
  const breaker = eventOutput(events, "size_breaker");
  let network = "TP 12-608";
  if (location?.feeder) {
    const kind = location.element_kind === "cabinet" ? "cabinet" : "pole";
    network = `TP 12-608, feeder ${location.feeder}, ${kind} ${location.element_id}`;
  }
  let proposed = "Pending";
  if (solution?.id) {
    const amps = breaker?.amps != null ? `${breaker.amps} A breaker` : "";
    const cable = solution.cable_mm2 ? `${solution.cable_mm2} mm² service` : "";
    if (solution.id === "A") proposed = amps ? `Breaker in the existing cabinet, ${amps}` : "Breaker in the existing cabinet";
    else if (solution.id === "C") proposed = ["Cable cut-in", cable, amps].filter(Boolean).join(", ");
    else proposed = ["New pole-mounted cabinet", cable, amps].filter(Boolean).join(", ");
  }
  return {
    power: `${power.kw} kW, ${power.phases === 1 ? "1-phase" : "3-phase"}`,
    coords: `${coordText(power.lat)}, ${coordText(power.lon)}`,
    network,
    solution: proposed,
  };
}

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
  const [mode, setMode] = useState("flow");
  const [powerDraft, setPowerDraft] = useState(null);
  const [caseRequest, setCaseRequest] = useState(null);
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
    setMode("flow");
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

  async function launch(body, custom) {
    setError("");
    setEvents([]);
    setSection3("");
    setRunningTool("parse_request");
    setSelected("parse_request");
    setInspectorOpen(true);
    setMode("flow");
    stopRef.current();
    try {
      const created = await postJSON("/api/runs", body);
      setCaseRequest(custom);
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
      throw e;
    }
  }

  function requestBody(power) {
    const text = `New household customer, ${power.kw} kW, ${power.phases === 1 ? "one phase" : "three phases"}, coordinates ${power.lat}, ${power.lon}.`;
    return {
      scenario_id: "intake",
      text,
      form: {
        kw: power.kw,
        phases: power.phases,
        lat: power.lat,
        lon: power.lon,
        object_name: power.objectName,
        customer_type: "household",
        text,
      },
    };
  }

  function start() {
    if (caseRequest) return launch(requestBody(caseRequest), caseRequest);
    return launch({ scenario_id: "hero", text: HERO.text, form: HERO }, null);
  }

  function loadPower(power) {
    stopRef.current();
    setError("");
    setEvents([]);
    setSection3("");
    setRunningTool(null);
    setRun(null);
    setSelected("parse_request");
    setInspectorOpen(false);
    setKindOverlay(false);
    setCaseRequest(power);
    setMode("flow");
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

  const summary = requestSummary(caseRequest, events);
  const issuedDoc = snap?.issued?.document || snap?.draft?.document;
  const waiting = status === "awaiting_approval";
  const hud = status === "running" || runningTool
    ? { cls: "run", text: `Running ${runningTool || "…"}` }
    : status === "awaiting_approval"
      ? { cls: "wait", text: "Awaiting engineer" }
      : status === "issued"
        ? { cls: "ok", text: snap?.issued?.ts_number || "Issued" }
        : status === "escalated"
          ? { cls: "wait", text: "Needs an engineer" }
          : !run && caseRequest
            ? { cls: "", text: `${caseRequest.kw} kW, ${caseRequest.phases}-phase, press Start` }
            : { cls: "", text: caseRequest ? `${caseRequest.kw} kW, ${caseRequest.phases}-phase` : "11 kW, 3-phase, L-200, pole 200/3" };

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
        mode={mode}
        onShowFlow={() => setMode("flow")}
        onShowRequest={() => setMode("request")}
        onShowPower={() => setMode("power")}
        onShowTest={() => setMode("test")}
        onApplyCase={(item) => {
          setPowerDraft({ ...item, stamp: Date.now() });
          setMode("power");
        }}
      />
      <section className="main">
        <header className="top">
          <div className="crumb" data-testid="app-title">
            <img src="/eso-logo.png" alt="" />
            ESO helper
          </div>
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
              Start
            </button>
          </div>
        </header>

        {mode === "request" ? (
          <ChangeRequest />
        ) : mode === "test" ? (
          <TestEnvironment />
        ) : mode === "power" ? (
          <PowerRequest busy={status === "running" || Boolean(runningTool)} draft={powerDraft} onSubmit={loadPower} />
        ) : (
        <>
        <div className="request-bar" data-testid="request-bar">
          <div><b>Requested power</b><span>{summary.power}</span></div>
          <div><b>Coordinates</b><span>{summary.coords}</span></div>
          <div><b>Network</b><span>{summary.network}</span></div>
          <div><b>Proposed solution</b><span>{summary.solution}</span></div>
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
                <div style={{ color: "var(--muted)", fontSize: 12 }}>§3, audit, issue</div>
              </div>
              <div style={{ display: "flex", gap: 8 }}>
                {run?.id && <a className="go" href={`/api/runs/${run.id}/audit.html`} target="_blank" rel="noreferrer">Audit</a>}
                <button className="go" type="button" onClick={saveEdit}>Save §3</button>
                <button className="exec" type="button" data-testid="approve" onClick={approve}>Approve and issue</button>
              </div>
            </div>
          )}
        </div>
        </>
        )}
      </section>
    </div>
  );
}

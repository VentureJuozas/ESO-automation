import { useEffect, useRef, useState } from "react";
import { GROUPS, STEP_LABEL } from "../steps.js";
import { Icon } from "../icons.jsx";

const TEST_CASES = [
  {
    id: "overload",
    title: "100 kW overload",
    note: "Fails the capacity check",
    objectName: "Large load",
    kw: "100",
    phases: "3",
    lat: "54.55929",
    lon: "25.27955",
  },
  {
    id: "household",
    title: "11 kW household",
    note: "Passes the load checks",
    objectName: "Household connection",
    kw: "11",
    phases: "3",
    lat: "54.55929",
    lon: "25.27955",
  },
];

function stepState(id, events, runningTool, status) {
  if (runningTool === id) return "run";
  const ev = [...events].reverse().find((e) => e.tool === id);
  if (!ev) return "wait";
  if (ev.type === "interrupt") return "stop";
  if (ev.outputs?.pass === false || ev.outputs?.escalate) return "stop";
  if (id === "issue_ts" && status !== "issued") return "wait";
  if (id === "engineer_approval" && status === "awaiting_approval") return "stop";
  return "done";
}

export default function Sidebar({
  events = [],
  runningTool,
  selected,
  onSelect,
  open,
  onToggle,
  status,
  mode = "flow",
  onShowFlow,
  onShowRequest,
  onShowPower,
  onShowTest,
  onApplyCase,
}) {
  const [flowOpen, setFlowOpen] = useState(false);
  const [casesOpen, setCasesOpen] = useState(true);
  const modeRef = useRef(mode);

  useEffect(() => {
    if (modeRef.current !== "flow" && mode === "flow") setFlowOpen(true);
    modeRef.current = mode;
  }, [mode]);

  return (
    <aside className="side" data-testid="sidebar">
      <div className="brand">
        <img className="brand-logo" src="/eso-logo.png" alt="ESO" />
        <div>
          <b>ESO helper</b>
          <small>0.4 kV, TP 12-608</small>
        </div>
      </div>
      <nav className="nav">
        <p className="nav-label">Main</p>
        <button
          className={`nav-item${mode === "flow" && flowOpen ? " on" : ""}`}
          type="button"
          data-testid="nav-flow"
          aria-expanded={flowOpen}
          onClick={() => {
            onShowFlow?.();
            setFlowOpen((value) => (mode !== "flow" ? true : !value));
          }}
        >
          <Icon name="branch" size={16} />
          Flow
          <i className={`nav-chev${flowOpen ? " open" : ""}`} aria-hidden="true" />
        </button>
        {flowOpen && (
          <div className="flow-body">
            {GROUPS.map((g) => (
              <div key={g.id} data-testid={`group-${g.id}`}>
                <button
                  className={`nav-sub${open[g.id] ? " on" : ""}`}
                  type="button"
                  aria-expanded={Boolean(open[g.id])}
                  onClick={() => onToggle(g.id)}
                >
                  <Icon name={g.icon} size={15} />
                  {g.title}
                  <i className={`nav-chev${open[g.id] ? " open" : ""}`} aria-hidden="true" />
                </button>
                {open[g.id] && g.tools.map((id) => {
                  const st = stepState(id, events, runningTool, status);
                  return (
                    <button
                      key={id}
                      className={`nav-step${selected === id ? " on" : ""}`}
                      type="button"
                      data-testid={`step-${id}`}
                      onClick={() => {
                        onShowFlow?.();
                        onSelect(id);
                      }}
                    >
                      <i className={`nav-dot st-${st}`} />
                      {STEP_LABEL[id] || id}
                    </button>
                  );
                })}
              </div>
            ))}
          </div>
        )}
        <button
          className={`nav-item${mode === "power" ? " on" : ""}`}
          type="button"
          data-testid="nav-power"
          aria-pressed={mode === "power"}
          onClick={() => onShowPower?.()}
        >
          <Icon name="doc" size={16} />
          New request
        </button>
        <button
          className={`nav-item${casesOpen ? " on" : ""}`}
          type="button"
          data-testid="nav-cases"
          aria-expanded={casesOpen}
          onClick={() => setCasesOpen((value) => !value)}
        >
          <Icon name="grid" size={16} />
          Test cases
          <i className={`nav-chev${casesOpen ? " open" : ""}`} aria-hidden="true" />
        </button>
        {casesOpen && (
          <div className="flow-body" data-testid="test-cases">
            {TEST_CASES.map((item) => (
              <button
                key={item.id}
                className={`case-row${item.id === "overload" ? " fail" : ""}`}
                type="button"
                data-testid={`case-${item.id}`}
                onClick={() => onApplyCase?.(item)}
              >
                <b>{item.title}</b>
                <small>{item.note}</small>
              </button>
            ))}
          </div>
        )}
        <button
          className={`nav-item${mode === "test" ? " on" : ""}`}
          type="button"
          data-testid="nav-test-env"
          aria-pressed={mode === "test"}
          onClick={() => onShowTest?.()}
        >
          <Icon name="flask" size={16} />
          Test environment
        </button>

        <p className="nav-label">Suggestions</p>
        <button
          className={`nav-item${mode === "request" ? " on" : ""}`}
          type="button"
          data-testid="nav-propose"
          aria-pressed={mode === "request"}
          onClick={() => onShowRequest?.()}
        >
          <Icon name="plus" size={16} />
          Propose a change
        </button>
      </nav>
    </aside>
  );
}
